import json
import pandas as pd


def rule_generator(issue):
    issue_user_login = issue['issueUserID']

    # Step 1: 2 dimensions of user profile
    def label_user_profile(user):
        # read_user_profile_data
        user_profile = pd.read_csv('./data/user_profile/issue_label_user_profile.csv')
        user_profile = user_profile.set_index('owner_login')
        mean_issue_num = user_profile['issue_num'].mean()

        if user in user_profile.index:
            # user_activity
            if user_profile['issue_num'][user] > mean_issue_num:
                user_activity = 'core_contributor'
            elif user_profile['issue_num'][user] == 1:
                user_activity = 'common_contributor'
            else:
                user_activity = 'common_user'
            # user_habit
            if user_profile['labeled_ratio'][user] >= 0.9:
                user_habit = 'excellent'
            elif 0.5 <= user_profile['labeled_ratio'][user] < 0.9:
                user_habit = 'average'
            else:
                user_habit = 'bad'
        else:
            user_activity = 'first_issuer'
            user_habit = 'none'

        return [user_activity, user_habit]

    issue_user_activity, issue_user_habit = label_user_profile(issue_user_login)
    print(f"{issue_user_login}: {issue_user_activity}, {issue_user_habit}")

    # Step 2: Iterable rule generators with user profile
    def info_rule_generator(user_activity, user_habit):
        user_rules = pd.read_csv('./data/rule_generator/issue_label_rule_generator.csv')
        user_rules = user_rules.set_index('user_habit')
        community_assignee_list = ['lizi', 'mfl']  # Community Maintainer

        with open("./data/rule_generator/info_text_template.json", 'r',  encoding='UTF-8') as load_f:
            info_text_template = pd.DataFrame(json.load(load_f)).set_index("infoType")

        execute_time = issue['issueUpdateTime']
        rules = []

        if user_activity == 'first_issuer' and user_habit == 'none':

            info_payload = {
                'targetUser': community_assignee_list,
                'infoType': 'issueComment',
                'infoContent': info_text_template['infoText']['assign_maintainer']
            }
            rule = {
                'issueID': issue['issueID'],
                'ruleType': 'info',
                'exeTime': execute_time,
                'infoPayload': info_payload
            }
            rules.append(rule)

        info_rule = json.loads(user_rules[user_activity][user_habit])
        # print(info_rule)

        info_payload = {
            'targetUser': issue_user_login,
            'infoType': info_rule['info_type'],
            'infoContent': info_text_template['infoText']['label_without_recommendation']
        }
        rule = {
            'issueID': issue['issueID'],
            'ruleType': 'info',
            'exeTime': execute_time,
            'infoPayload': info_payload
        }
        rules.append(rule)

        return rules

    # def action_rule_generator(user_activity, user_habit):
    #     pass

    info_rules = info_rule_generator(issue_user_activity, issue_user_habit)

    # Step 3: Generate the complete rule list
    rule_list = info_rules
    return rule_list


if __name__ == "__main__":
    issue_str = '{"issueID":"issueIDabc123", ' \
                '"issueAction":"issueAction：Create、Del...",' \
                '"issueUser":"david-he9",' \
                '"issueUserID":"issueUserIDabc123",' \
                '"issueTime":"RFC3399",' \
                '"issueUpdateTime":"2021-10-14T20:26:30+08:00",' \
                '"issueAssignee":"用户ID？",' \
                '"issueLabel":["SIG/XX", "kind/bug"]}'
    test_issue = json.loads(issue_str)
    print(rule_generator(test_issue))
