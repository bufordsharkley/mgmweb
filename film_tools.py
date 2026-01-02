#!/bin/sh
""":"
exec uv run --project "$(dirname "$0")" python "$0" "$@" #
"""

import datetime
import itertools
import random

import click
import yaml

from mgmweb import film_logic

TIERS = ['I', 'II-A', 'II-B', 'II-C', 'III-A', 'III-B', 'III-C', 'IV']
FULL_TIERS = ['I', 'II-Aa', 'II-A', 'II-B', 'II-C', 'III-A', 'III-B', 'III-C', 'IV']


@click.group()
def main():
    pass


@main.command()
def check():
    """Basic vetting for master yaml."""
    master = get_master()
    for month in master:
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
    master, error_log = film_logic.flesh_out_rewatches(master, log_errors=True)
    # TODO: check stubz against being sequential, and in the correct month
    # and possibly sanity checks of repeated days?
    if False:  # I don't use this anymore, should remove:
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
@click.option('--month', default='LAST', help="month to list, format='yyyy-mm'")
def current(month):
    """Print current, in-progress month, so to create new list."""

    def print_month_contents(month):
        print(f"#{month['month']}")
        films = month['films']
        for film in films:
            if 'filter' in film:
                continue
            if 'rewatch' in film:
                directors = ', '.join(film['director'])
                print(f"*{film['rewatch']} ({directors}, {film['year']})")
            else:
                directors = ', '.join(film['director'])
                print(f"{film['title']} ({directors}, {film['year']})")
        print(len(films))

    master = get_master()
    master = film_logic.flesh_out_rewatches(master)
    if month == 'LAST':
        for month in master:
            if month['status'] != ('in-progress'):
                continue
            print_month_contents(month)
    else:
        target = datetime.datetime.strptime(month, "%Y-%m").strftime("%B %Y")
        for month in master:
            if month['month'] != target:
                continue
            print_month_contents(month)


def get_tiers_for_year(year, master, no_tier=False):
    tiers_for_year = {tier: [] for tier in FULL_TIERS}
    if no_tier:
        tiers_for_year['NONE'] = []
    for month in master:
        for film in month['films']:
            if 'filter' in film or 'title' not in film:
                continue
            try:
                film_year = film['effective_year']
            except KeyError:
                film_year = film['year']
            if film_year == year:
                try:
                    tier = film['tier']
                    film['month'] = month['month']
                    tiers_for_year[tier].append(film)
                except KeyError:
                    if no_tier:
                        tiers_for_year['NONE'].append({'title': film['title']})
                    print(f'No Tier for {film["title"]}')
                    continue
    return tiers_for_year


@main.command()
@click.option('--tier', default="II-B", help="tier or higher to recommend from")
@click.option('--num', default=1, help="number of reccs")
@click.option('--yearsort', is_flag=True, default=False, help="sort by year")
@click.option('--randomold', is_flag=True, default=False, help="Random old one")
@click.option('--completechrono', is_flag=True, default=False, help="complete for tier")
def reccs(tier, num, yearsort, randomold, completechrono):
    if randomold:
        master = get_master()
        all_possible_reccs = []
        for month in master:
            year = int(month['month'].split()[-1])
            if year > 2014:
                continue
            for film in month['films']:
                if 'title' in film:
                    directors = ', '.join(film['director'])
                    film_str = (f"{film['title']} ({directors}, {film['year']})")
                    all_possible_reccs.append(film_str)
        random.shuffle(all_possible_reccs)
        print(all_possible_reccs[0])
        return
    master = get_master()
    if tier != 'ALL':
        idx = FULL_TIERS.index(tier)
        tiers = FULL_TIERS[:idx + 1]
        if completechrono:
            tiers = [tier]
    all_possible_reccs = []
    decades = {x: 0 for x in ('1910s', '1920s', '1930s', '1940s', '1950s', '1960s', '1970s', '1980s')}
    for month in master:
        for film in month['films']:
            if 'tier' in film and (tier == 'ALL' or film['tier'] in tiers) and 'title' in film:
                directors = ', '.join(film['director'])
                year = film['year']
                film_str = (f"{film['title']} ({directors}, {year})")
                if 1910 <= year < 1920:
                    decades['1910s'] += 1
                elif 1920 <= year < 1930:
                    decades['1920s'] += 1
                elif 1930 <= year < 1940:
                    decades['1930s'] += 1
                elif 1940 <= year < 1950:
                    decades['1940s'] += 1
                elif 1950 <= year < 1960:
                    decades['1950s'] += 1
                elif 1960 <= year < 1970:
                    decades['1960s'] += 1
                elif 1970 <= year < 1980:
                    decades['1970s'] += 1
                elif 1980 <= year < 1990:
                    decades['1980s'] += 1
                all_possible_reccs.append(film_str)
    for k, v in decades.items():
        print(f"{k}: {v}")
    if completechrono:
        assert tier in FULL_TIERS
        print('\n'.join(sorted(all_possible_reccs, key=lambda x: x.rsplit(' ', 1)[1])))
        return
    if not yearsort:
        random.shuffle(all_possible_reccs)
        print('\n'.join(x for x in all_possible_reccs[:num]))
    else:
        print('\n'.join(x for x in sorted(all_possible_reccs, key=lambda x: x.rsplit(',', 1)[1])))




@main.command()
@click.argument('year', default=datetime.datetime.now().year)
@click.option('--merge', is_flag=True, default=False, help="merge sort")
@click.option('--diff', is_flag=True, default=False, help="check against ranking list")
def year(year, merge, diff):
    """Print all films for a year (corrected for effective year)"""
    goal_year = int(year)
    master = get_master()

    gather_no_tier = False if not diff else True
    tiers_for_year = get_tiers_for_year(goal_year, master, no_tier=gather_no_tier)
    total_count = sum(len(x) for x in tiers_for_year.values())

    final_merged = {}
    if diff:
        ranked = set(x.strip() for x in
                     open(f'/home/mgm/repos/filmcanon_scripts/{year}ranking.txt').readlines())

        all_films = set()
        for tier in tiers_for_year.values():
            for film in tier:
                all_films.add(film['title'])
        print(all_films - ranked)
        print(all_films, ranked)
        return
    for tier, films in tiers_for_year.items():
        # This is an absolute nightmare, it sorts and then uses groupby to 
        # bunch the same movies per tier from the same month:
        def _sort_ranking_key(film):
            try:
                return film['ranking']
            except KeyError:
                return 999
        months_per_tier = [
            [film['title'] for film in sorted(group, key=_sort_ranking_key)]
             for key, group in itertools.groupby(sorted(films,
                key=lambda x: x['month']), lambda x: x['month'])]
        if not months_per_tier:
            final_merged[tier] = []
            continue
        if not merge:
            print(tier)
            print('\n*\n'.join('\n'.join(x) for x in months_per_tier))
        else:
            output = merge_sort(months_per_tier)
            print(output)
            final_merged[tier] = output
            """
            output = []
            while len(month_traunches) >= 2:
                tops = {ii + 1: x[0] for ii, x in enumerate(month_traunches)}
                prompt = '\n'.join(f'{ii}. {x}' for ii, x in tops.items())
                print(prompt)
                value = click.prompt('Pick top choice', type=int)
                output.append(month_traunches[value - 1].pop(0))
                month_traunches = [x for x in month_traunches if x]
            output.append(month_traunches[0].pop(0))
            final_merged[tier] = output
            """
    if merge:
        for tier, films in final_merged.items():
            print(tier)
            print('\n'.join(films))
    print(f"Total count: {total_count}")


def merge_sort(months):
    def merge_sort_two(months):
        resp = []
        while len(months) > 1:
            tops = {ii + 1: x[0] for ii, x in enumerate(months)}
            prompt = '\n'.join(f'{ii}. {x}' for ii, x in tops.items())
            print(prompt)
            value = click.prompt('Pick top choice', type=int)
            resp.append(months[value - 1].pop(0))
            months = [x for x in months if x]
        resp.extend(months[0])
        return resp

    random.shuffle(months)
    print(months)
    if len(months) == 1:
        return months[0]
    elif len(months) == 2:
        #return merge_sort_two(*months)
        return merge_sort_two(months)
    else:
        while len(months) > 2:
            print(f"{len(months)} to merge")
            #merged = merge_sort_two(*months[:2])
            merged = merge_sort_two(months[:2])
            months = [merged, *months[2:]]
            random.shuffle(months)
        return merge_sort_two(months)
        #return merge_sort_two(*months)


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
        print(month_txt)
        ranking = lists[month_txt]
        month_status = master_data['status']
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
        if month_status == 'in-progress':
            master_data['status'] = 'ranked'
        elif month_status == 'tier norank':
            master_data['status'] = 'ranked approx'
        else:
            raise NotImplementedError
        out_master.append(master_data)
    output_text = yaml.dump(out_master, sort_keys=False, allow_unicode=True)
    print("Updated yaml document: /tmp/master_updated.yaml")
    with open('/tmp/master_updated.yaml', 'w') as f:
        f.write(output_text)


@main.command()
@click.argument('month', nargs=-1, required=True)
@click.option('--raw', is_flag=True, default=False,
              help="show raw rankings, avoid rewatch merge")
def ranking(month, raw):
    """Print ranking for certain month."""
    master = get_master()
    # Important here to get info on director for rewatches:
    master = film_logic.flesh_out_rewatches(master)
    if month[0] == 'ALL':
        for month_data in master:
            if month_data['status'] != 'ranked':
                continue
            print(month_data['month'])
            print_month(month_data, raw)
    else:
        month = " ".join(month)
        month_data = [x for x in master if x['month'] == month][0]
        print_month(month_data, raw)


def print_month(month_data, raw=False):
    tiers = film_logic.organize_month_data_into_tiers(month_data, raw)
    for tier, payload in tiers:
        print(tier)
        print("\n".join(payload))
        print()

if __name__ == "__main__":
    main()
