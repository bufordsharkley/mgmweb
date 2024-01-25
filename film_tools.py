#!/usr/bin/python3

import itertools

import click
import yaml

TIERS = ['I', 'II-A', 'II-B', 'II-C', 'III-A', 'III-B', 'III-C', 'IV']


@click.group()
def main():
    pass


@main.command()
def check():
    """Basic vetting for master yaml."""
    master = get_master()
    for month in master:
        print(month['month'])
        assert month['status'] in ('unranked', 'ranked', 'tier norank')
        rankings = False
        films = month['films']
        for film in films:
            if film.get('filter', False):
                continue
            if 'title' in film:
                assert 'year' in film
                assert 'director' in film
                assert type(film['director']) == list
            elif 'rewatch' in film:
                assert '(' in film['rewatch']
            else:
                raise Exception(film)
            if 'ranking' in film:
                rankings = True
        if rankings and not month['status'] == 'unranked':
            assert all('ranking' in film for film in films if not 'filter' in film)
            print('-------------RANKED-------------')
        else:
            print('************ UNRANKED***********')
        print(len(films))
        print()


def get_master():
    return yaml.load(open('mgmweb/static/master.yaml'), Loader=yaml.FullLoader)


@main.command()
def current():
    """Print current, in-progress month, so to create new list."""
    master = get_master()
    for month in master:
        if month['status'] != ('in-progress'):
            continue
        print(f"#{month['month']}")
        films = month['films']
        for film in films:
            if 'rewatch' in film:
                print(f"*{film['rewatch']}")
            else:
                directors = ', '.join(film['director'])
                print(f"{film['title']} ({directors}, {film['year']})")
        print(len(films))


def pre_process(lines):
    """Mostly unsplit multiple tiers corresponding to (none)"""
    for line in lines:
        line = line.strip()
        chunks = line.split(', ')
        if len(chunks) == 1:
            yield line
            continue
        if chunks[-1][-1] == ':':
            chunks[-1] = chunks[-1][:-1]
        if all(x in TIERS for x in chunks):
            for chunk in chunks[:-1]:
                yield chunk
                yield ('(none)')
            yield chunks[-1]
        else:
            yield line


def check_lists(lists):
    raise Exception("I haven't tried this yet, be gentle.")
    for month, tiers in lists.items():
        keys = tiers.keys()
        extra = set(keys) - set(TIERS)
        if extra:
            raise Exception(f"extra tiers: {extra}")
        missing = set(TIERS) - set(keys)
        if missing:
            raise Exception(f"missing in {month}: {missing}")


def get_lists(filename):
    curr_month = None
    resp = {}
    lines = open(filename).readlines()
    lines = pre_process(lines)
    for line in lines:
        if not line:
            continue
        if line.startswith('#'):
            line = line[1:].strip()
            month = line.capitalize()
            if month[-1] == ':':
                month = month[:-1]
            curr_month = month
            resp[curr_month] = {}
            curr_tier = None
        elif line[0] in ('0123456789'):
            num, film = line.split('.', 1)
            num = int(num)
            film = film.rsplit(' (', 1)[0]
            film = film.strip()
            film = film.replace("’", "'")
            if film[0] == '*':
                film = film[1:].strip()
            resp[curr_month][curr_tier].append((num, film))
        elif line in TIERS:
            if curr_month is None:
                raise RuntimeError("Need to specify #MONTH YEAR at top of list")
            curr_tier = line
            if curr_tier in resp[curr_month]:
                raise Exception(curr_tier, resp[curr_month])
            resp[curr_month][curr_tier] = []
        elif line == '(none)':
            pass
        else:
            raise Exception(line)
    return resp


def find_master_film(film_to_find, master_data):
    def is_right_film(film, film_to_find):
        if 'title' in film:
            if film['title'] == film_to_find:
                return True
        elif 'rewatch' in film:
            if film['rewatch'].split(' (')[0].lower() == film_to_find.lower():
                return True
        return False
    title_find = [film for film in master_data
                  if is_right_film(film, film_to_find)]
    if not title_find:
        raise Exception(f'cannot find {film_to_find}')
    assert len(title_find) == 1
    return title_find[0]


@main.command()
@click.argument('filename', type=click.Path(exists=True))
def newlist(filename):
    """Feed new monthly list(s) and create new yaml master in /tmp"""
    lists = get_lists(filename)
    check_lists(lists)
    out_master = []
    master = get_master()
    for master_data in master:
        month_txt = master_data['month']
        if month_txt not in lists:
            out_master.append(master_data)
            continue
        ranking = lists[month_txt]
        assert master_data['status'] in ('unranked', 'in-progress')
        print(month_txt)
        master_films = master_data['films']
        count = {tier: 0 for tier in TIERS}
        for tier, num_films in ranking.items():
            for num, film in num_films:
                print(num, film)
                master_film = find_master_film(film, master_films)
                master_film['ranking'] = num
                master_film['tier'] = tier
                count[tier] += 1
        master_data['tiers'] = count
        master_data['status'] = 'ranked'
        out_master.append(master_data)
    output_text = yaml.dump(out_master, sort_keys=False, allow_unicode=True)
    print("Updated yaml document: /tmp/master_updated.yaml")
    with open('/tmp/master_updated.yaml', 'w') as f:
        f.write(output_text)



def flesh_out_rewatches(master):
    # First, list of all rewatches
    rewatches = set()
    for month in master:
        for film in month['films']:
            if film.get('filter', False):
                continue
            if 'rewatch' in film:
                rewatch, year = film['rewatch'].rsplit(' (', 1)
                year = int(year[:-1])
                rewatches.add((rewatch, year))
    fixes = {k: None for k in rewatches}
    for month in master:
        for film in month['films']:
            if film.get('filter', False) or not 'title' in film:
                continue
            title, year = film['title'], film['year']
            if (title, year) in rewatches:
                fixes[(title, year)] = {'director': film['director']}
    for month in master:
        for film in month['films']:
            if film.get('filter', False):
                continue
            if 'rewatch' in film:
                rewatch, year = film['rewatch'].rsplit(' (', 1)
                year = int(year[:-1])
                film['rewatch'] = rewatch
                film['year'] = year
                film['director'] = fixes[(rewatch, year)]['director']
    return master



@main.command()
@click.argument('month', nargs=-1, required=True)
def ranking(month):
    """Print ranking for certain month."""
    master = get_master()
    # Important here to get info on director for rewatches:
    master = flesh_out_rewatches(master)
    if month[0] == 'ALL':
        for month_data in master:
            if month_data['status'] != 'ranked':
                continue
            print(month_data['month'])
            print_month(month_data)
    else:
        month = " ".join(month)
        month_data = [x for x in master if x['month'] == month][0]
        print_month(month_data)


def print_month(month_data):
    if 'status' not in month_data:
        print("NOT RANKED")
        return
    tiers = month_data['tiers']
    check_tiers(tiers, month_data)
    raw_rankings = {}
    for film in month_data['films']:
        if 'filter' in film:
            continue
        raw_rankings[film['ranking']] = film
    num_real_films = sum(1 for x in month_data['films'] if 'filter' not in x)
    assert num_real_films == sum(tiers.values())
    assert len(raw_rankings.keys()) == num_real_films
    if set(raw_rankings.keys()) == {ii + 1 for ii in range(num_real_films)}:
        rankings = raw_rankings
        pass
    else:
        rankings = {}
        real_rank_set = {ii + 1 for ii in range(num_real_films)}
        for old, new in zip(sorted(raw_rankings.keys()), sorted(real_rank_set)):
            rankings[new] = raw_rankings[old]
    curr = 1
    for is_empty, group in itertools.groupby(tiers.items(),
                                             key=lambda x: x[1]==0):
        group_list = list(group)
        if is_empty:
            if len(group_list) == 1:
                print(group_list[0][0] + ":")
                print("(none)")
            else:
                print(", ".join(x[0] for x in group_list) + ":")
                print("(none)")

            print()
        else:
            for tier, count in group_list:
                print(tier + ":")
                for ii in range(count):
                    rank = curr + ii
                    film = rankings[rank]
                    print(f"{rank}. ", end="")
                    if 'title' in film:
                        title = film['title']
                        director = ", ".join(film['director'])
                        year = film['year']
                        print(f"{title} ({director}, {year})")
                    elif 'ranking' in film:
                        director = ", ".join(film['director'])
                        year = film['year']
                        print(f"* {film['rewatch']} ({director}, {year})")
                    else:
                        raise Exception(film)
                curr += count
                print()


def check_tiers(tiers, month_data):
    """putting in tiers was a mistake, whoops"""
    new_tiers = {x: 0 for x in ('I', 'II-A', 'II-B', 'II-C', 'III-A', 'III-B', 'III-C', 'IV')}
    for film in month_data['films']:
        if 'filter' in film:
            continue
        tier = film['tier']
        if tier == 'II-Aa':
            tier = 'II-A'
        new_tiers[tier] += 1
    if new_tiers != tiers:
        print(new_tiers)
        print(tiers)
        raise Exception("The tiered component doesn't match. Is this important?")

if __name__ == "__main__":
    main()
