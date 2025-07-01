import itertools


def get_chrono_reccs(films):
    tier = 'I'
    reccs = {'I': [], 'II-Aa': [], 'II-A': []}
    for month in films:
        for film in month['films']:
            if film.get('filter', False):
                continue
            if 'title' not in film:
                continue
            if 'tier' in film and film['tier'] == 'I':
                reccs['I'].append(film)
                reccs['II-Aa'].append(film)
                reccs['II-A'].append(film)
            elif 'tier' in film and film['tier'] == 'II-Aa':
                reccs['II-Aa'].append(film)
                reccs['II-A'].append(film)
            elif 'tier' in film and film['tier'] == 'II-A':
                reccs['II-A'].append(film)
    for films in reccs.values():
        films.sort(key=lambda x: x['year'])
    return reccs


def flesh_out_rewatches(master, log_errors=False):
    # First, list of all rewatches
    rewatches = set()
    tier_tracker = {}
    error_log = []
    for month in master:
        for film in month['films']:
            if film.get('filter', False):
                continue
            if 'rewatch' in film:
                rewatch, year = film['rewatch'].rsplit(' (', 1)
                year = int(year[:-1])
                if (rewatch, year) in rewatches:
                    # Things are actually okay, just want to check:
                    raise Exception((rewatch, year))
                rewatches.add((rewatch, year))
                try:
                    tier_tracker[(rewatch, year)] = film['tier']
                except KeyError:
                    pass  # Oh, it's for diffs, right.. for error checking
    print(tier_tracker)
    fixes = {k: None for k in rewatches}
    for month in master:
        for film in month['films']:
            if film.get('filter', False) or not 'title' in film:
                continue
            title, year = film['title'], film['year']
            if (title, year) in rewatches:
                fixes[(title, year)] = {'director': film['director']}
                try:
                    orig_tier = film['tier']
                except KeyError:
                    orig_tier = 'G'
                    print(film)
                try:
                    new_tier = tier_tracker[(title, year)]
                except KeyError:
                    orig_tier = 'OOP'
                    new_tier = 'WHOOP'
                if orig_tier != new_tier:
                    print(title, year)
                    print(new_tier, orig_tier)
    for month in master:
        for film in month['films']:
            if film.get('filter', False):
                continue
            if 'rewatch' in film:
                rewatch, year = film['rewatch'].rsplit(' (', 1)
                year = int(year[:-1])
                film['rewatch'] = rewatch
                film['year'] = year
                try:
                    film['director'] = fixes[(rewatch, year)]['director']
                except TypeError:
                    raise Exception(f"Can't find original for {rewatch} ({year})")
    if log_errors:
        return master, error_log
    else:
        return master


def _check_tiers(tiers, month_data):
    """putting in tiers was a mistake, whoops"""
    new_tiers = {x: 0 for x in ('I', 'II-A', 'II-B', 'II-C',
                                'III-A', 'III-B', 'III-C', 'IV')}
    for film in month_data['films']:
        if 'filter' in film:
            continue
        tier = film['tier']
        if tier == 'II-Aa':
            tier = 'II-A'
        new_tiers[tier] += 1
    if new_tiers != tiers:
        print(month_data['month'])
        print(new_tiers)
        print(tiers)
        raise Exception("Tiered component doesn't match. Is this important?")


def organize_month_data_into_tiers(month_data, raw=False):
    tiers = month_data['tiers']
    if not raw:
        _check_tiers(tiers, month_data)
    raw_rankings = {}
    for film in month_data['films']:
        if 'filter' in film:
            continue
        raw_rankings[film['ranking']] = film
    num_real_films = sum(1 for x in month_data['films'] if 'filter' not in x)
    # I suppose these should have been in the check, but oh well
    assert num_real_films == sum(tiers.values())
    assert len(raw_rankings.keys()) == num_real_films
    if set(raw_rankings.keys()) == {ii + 1 for ii in range(num_real_films)}:
        rankings = raw_rankings
    else:  # Basically cases in which films have been re-ranked:
        rankings = {}
        real_rank_set = {ii + 1 for ii in range(num_real_films)}
        for old, new in zip(sorted(raw_rankings.keys()), sorted(real_rank_set)):
            rankings[new] = raw_rankings[old]
    resp = []
    curr = 1
    for is_empty, group in itertools.groupby(tiers.items(),
                                             key=lambda x: x[1] == 0):
        group_list = list(group)
        if is_empty:
            if len(group_list) == 1:
                tier_key = group_list[0][0] + ":"
            else:
                tier_key = ", ".join(x[0] for x in group_list) + ":"
            resp.append((tier_key, ["(none)"]))
        else:
            for tier, count in group_list:
                tier_key = tier + ":"
                film_list = []
                for ii in range(count):
                    rank = curr + ii
                    film = rankings[rank]
                    director = ", ".join(film['director'])
                    year = film['year']
                    raw_ranking = film['ranking']
                    # Assume title or rewatch only keys
                    title = film['title'] if 'title' in film else f"* {film['rewatch']}"
                    if raw:
                        film_str = f"{rank}. {title} ({director}, {year}) ({raw_ranking})"
                    else:
                        film_str = f"{rank}. {title} ({director}, {year})"
                    film_list.append(film_str)
                curr += count
                resp.append((tier_key, film_list))
    return resp
