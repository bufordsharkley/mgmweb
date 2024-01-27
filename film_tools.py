#!/usr/bin/python3

import click
import yaml

from mgmweb import film_logic

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
            if 'filter' in film:
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
    master = film_logic.flesh_out_rewatches(master)
    for month in master:
        if month['status'] != ('in-progress'):
            continue
        print(f"#{month['month']}")
        films = month['films']
        for film in films:
            if 'rewatch' in film:
                directors = ', '.join(film['director'])
                print(f"*{film['rewatch']} ({directors}, {film['year']})")
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


@main.command()
@click.argument('month', nargs=-1, required=True)
def ranking(month):
    """Print ranking for certain month."""
    master = get_master()
    # Important here to get info on director for rewatches:
    master = film_logic.flesh_out_rewatches(master)
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
    tiers = film_logic.organize_month_data_into_tiers(month_data)
    for tier, payload in tiers:
        print(tier)
        print("\n".join(payload))
        print()

if __name__ == "__main__":
    main()
