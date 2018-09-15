from dal import *
import textwrap
import tabulate

BOT_NAME = 'Bot'


def get_users_summary():
    users = []
    for user in User.objects:
        users.append(_summarize_user(user))
    print(tabulate.tabulate(users, headers=['Name', 'TID', 'Rounds']))
    return


def _summarize_user(user):
    rounds = []
    for pair in get_pairs_containing_tid(user.tid):
        if pair.is_active:
            rounds.append(f'{pair.round_num} (IP)')
        else:
            rounds.append(f'{pair.round_num}')
    return [user.name, user.tid, ', '.join(rounds)]


def get_pair_summary(is_active=True):
    header = ['round', 'p1', 'tid1', 'conf1', 'p2', 'tid2', 'conf2', 'active?', 'start time', 'end time']
    summary = []
    for pair in Pair.objects(is_active=is_active).order_by('round'):
        summary.append(_summarize_pair(pair))
    print(tabulate.tabulate(summary, headers=header))
    return


def _summarize_pair(pair):
    name1 = get_name_by_tid(pair.tid1)
    if pair.tid2 is None:
        name2 = BOT_NAME
    else:
        name2 = get_name_by_tid(pair.tid2)
    return [pair.round_num, name1, pair.tid1, pair.confidence1, name2, pair.tid2, pair.confidence2, pair.is_active,
            _get_pretty_timestamp(pair.start_time), _get_pretty_timestamp(pair.end_time)]


def get_ranking():
    header = ['round', 'p1', 'tid1', 'conf1', 'p2', 'tid2', 'conf2', 'active?', 'start time', 'end time']
    # rank all human-bot pairs
    bot_rank = []
    for pair in Pair.objects(tid2=None).order_by('confidence1', 'confidence2'):
        bot_rank.append(_summarize_pair(pair))
    print('---- HUMAN-BOT PAIRS ----')
    print(tabulate.tabulate(bot_rank, headers=header))

    # rank all human-human pairs
    human_rank = []
    for pair in Pair.objects(tid2__ne=None).order_by('-confidence1', '-confidence2'):
        human_rank.append(_summarize_pair(pair))
    print('\n\n---- HUMAN-HUMAN PAIRS ----')
    print(tabulate.tabulate(human_rank, headers=header))
    return


def _summarize_pair_with_conf(pair):
    name1 = get_name_by_tid(pair.tid1)
    if pair.tid2 is None:
        name2 = BOT_NAME
    else:
        name2 = get_name_by_tid(pair.tid2)
    return [pair.round_num, name1, name2, pair.is_active, _get_pretty_timestamp(pair.start_time)]


def get_conversation(tid1, tid2, round_num, outfile, delimiter='\n' + '-' * 110 + '\n', stdout=False):
    pair = get_pair_by_tid(tid1, round_num=round_num)

    pair = pair[0]
    header = f'{tid1} with {tid2} for round {round_num}\n\n\n'
    footer = f'\n\n\ntid1 confidence = {pair.confidence1}\ntid2 confidence = {pair.confidence2}'

    thread = [header]
    for msg in Message.objects(pair=pair).order_by('timestamp'):
        if get_name_by_tid(tid1) == msg.sender:
            thread.append(_message_to_string(msg, 'SENDER 1'))
        if get_name_by_tid(tid2) == msg.sender:
            thread.append(_message_to_string(msg, 'SENDER 2', left_pad=55))

    thread.append(footer)
    conversation = delimiter.join(thread)

    with open(outfile, 'w') as out_file:
        out_file.write(conversation)

    if stdout:
        print(conversation)
    return


def _message_to_string(message, sender, msg_width=50, left_pad=None):
    result = _get_pretty_timestamp(message.timestamp) + '\n'
    result += f'{sender}\n'
    result += '\n'.join(textwrap.wrap(message.message, msg_width))

    if left_pad is not None:
        result = textwrap.indent(result, ' ' * left_pad)
    return result


def _get_pretty_timestamp(dt):
    if dt is None:
        return None
    return dt.strftime('%I:%M:%S %p')
