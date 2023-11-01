#!/usr/bin/python3

import click
import yaml

TIERS = ['I', 'II-A', 'II-B', 'II-C', 'III-A', 'III-B', 'III-C', 'IV']


@click.group()
def main():
    pass


@main.command()
def check():
    raise NotImplementedError

def get_master():
    return yaml.load(open('mgmweb/static/master.yaml'), Loader=yaml.FullLoader)


@main.command()
def current():
    master = get_master()
    for month in master:
        if month['status'] != ('in-progress'):
            continue
        print(month['month'])
        films = month['films']
        for film in films:
            if 'rewatch' in film:
                print(film['rewatch'])
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
def ranklist(filename):
    lists = get_lists(filename)
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


if __name__ == "__main__":
    main()
