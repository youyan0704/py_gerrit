# -*- coding: utf-8 -*-
# @Time    : 19-5-8 下午4:08
# @Author  : allen.you

"""
    封装gerrit SSH-COMMANFS
    首先需要配置~/.ssh/config
    如： host gerrit别名
        user gerrit用户名
        port 29418
        hostname xxx.xxx.xxx.xxx
        identityFile ~/.ssh/id_rsa
"""
from __future__ import absolute_import
import logging
import subprocess
from .models import User

log = logging.getLogger(__name__)


class GerritSSHCommands(object):

    def __init__(self, server):
        self.__server = server
        self.__command = 'ssh {} gerrit %s '.format(self.__server)

    def run_gerrit_command(self, command, *args, **kwargs):
        """
        param: command, gerrit命令
        param: args, gerrit命令必须参数
        param： kwargs, gerrit命令可选参数，注意当参数key存在中划线‘-’时，使用下划线‘_’代替
        """
        if kwargs.get('trace') and not kwargs.get('trace_id'):
            raise Exception('--trace_id (can only be set if --trace was set too)')

        commands = self.__command % command
        for a in args:
            commands = commands + '%s ' % a

        for k in kwargs.items():
            commands = commands + '--%s %s ' % (k[0].replace('_', '-'), k[1])
        try:
            status, data = subprocess.getstatusoutput(commands)
        except Exception as err:
            raise Exception('Command execution error: %s' % err)
        if status != 0:
            print(status, data)
        return status, data

    def ban_commit(self, project, commit, **kwargs):
        """
            gerrit ban-commit PROJECT COMMIT ... [--] [--help (-h)] [--reason (-r) REASON] [--trace] [--trace-id VAL]

             PROJECT              : name of the project for which the commit should be
                                    banned
             COMMIT               : commit(s) that should be banned
             --                   : end of options (default: false)
             --help (-h)          : display this help text
             --reason (-r) REASON : reason for banning the commit
             --trace              : enable request tracing (default: false)
             --trace-id VAL       : trace ID (can only be set if --trace was set too)

        """

        status, data = self.run_gerrit_command('ban-commit', project, commit, **kwargs)

        return status, data

    def close_connection(self, session_id, **kwargs):
        """
            gerrit close-connection SESSION_ID ... [--] [--help (-h)] [--trace] [--trace-id VAL] [--wait]

             SESSION_ID     : List of SSH session IDs to be closed
             --             : end of options (default: false)
             --help (-h)    : display this help text
             --trace        : enable request tracing (default: false)
             --trace-id VAL : trace ID (can only be set if --trace was set too)
             --wait         : wait for connection to close before exiting (default: false)

        """
        self.run_gerrit_command('close-connection', session_id, **kwargs)

    def create_account(self, username, **kwargs):
        """
            gerrit create-account USERNAME [--] [--email EMAIL] [--full-name NAME] [--group (-g) GROUP] [--help (-h)] [--http-password PASSWORD] [--ssh-key -|KEY] [--trace] [--trace-id VAL]

             USERNAME                 : name of the user account
             --                       : end of options (default: false)
             --email EMAIL            : email address of the account
             --full-name NAME         : display name of the account
             --group (-g) GROUP       : groups to add account to
             --help (-h)              : display this help text (default: true)
             --http-password PASSWORD : password for HTTP authentication
             --ssh-key -|KEY          : public key for SSH authentication
             --trace                  : enable request tracing (default: false)
             --trace-id VAL           : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('create_account', username, **kwargs)

        return status, data


    def create_project(self, project, **kwargs):
        """
            gerrit create-project [NAME] [--] [--branch (-b) BRANCH] [--change-id [TRUE | FALSE | INHERIT]] [--content-merge [TRUE | FALSE | INHERIT]] [--contributor-agreements [TRUE | FALSE | INHERIT]] [--create-new-change-for-all-not-in-target (--ncfa)] [--description (-d) DESCRIPTION] [--empty-commit] [--help (-h)] [--max-object-size-limit VAL] [--new-change-for-all-not-in-target [TRUE | FALSE | INHERIT]] [--owner (-o) GROUP] [--parent (-p) NAME] [--permissions-only] [--plugin-config VAL] [--reject-empty-commit [TRUE | FALSE | INHERIT]] [--require-change-id (--id)] [--signed-off-by [TRUE | FALSE | INHERIT]] [--submit-type (-t) [INHERIT | FAST_FORWARD_ONLY | MERGE_IF_NECESSARY | REBASE_IF_NECESSARY | REBASE_ALWAYS | MERGE_ALWAYS | CHERRY_PICK]] [--suggest-parents (-S)] [--trace] [--trace-id VAL] [--use-content-merge] [--use-contributor-agreements (--ca)] [--use-signed-off-by (--so)]

             NAME                                   : name of project to be created
             --                                     : end of options (default: false)
             --branch (-b) BRANCH                   : initial branch name
                                                      (default: master)
             --change-id [TRUE | FALSE | INHERIT]   : if change-id is required (default:
                                                      INHERIT)
             --content-merge [TRUE | FALSE |        : allow automatic conflict resolving
             INHERIT]                                 within files (default: INHERIT)
             --contributor-agreements [TRUE |       : if contributor agreement is required
             FALSE | INHERIT]                         (default: INHERIT)
             --create-new-change-for-all-not-in-tar : if a new change will be created for
             get (--ncfa)                             every commit not in target branch
             --description (-d) DESCRIPTION         : description of project (default: )
             --empty-commit                         : to create initial empty commit
                                                      (default: false)
             --help (-h)                            : display this help text
             --max-object-size-limit VAL            : max Git object size for this project
             --new-change-for-all-not-in-target     : if a new change will be created for
             [TRUE | FALSE | INHERIT]                 every commit not in target branch
                                                      (default: INHERIT)
             --owner (-o) GROUP                     : owner(s) of project
             --parent (-p) NAME                     : parent project
             --permissions-only                     : create project for use only as parent
                                                      (default: false)
             --plugin-config VAL                    : plugin configuration parameter with
                                                      format '<plugin-name>.<parameter-name>
                                                      =<value>'
             --reject-empty-commit [TRUE | FALSE |  : if empty commits should be rejected
             INHERIT]                                 on submit (default: INHERIT)
             --require-change-id (--id)             : if change-id is required
             --signed-off-by [TRUE | FALSE |        : if signed-off-by is required
             INHERIT]                                 (default: INHERIT)
             --submit-type (-t) [INHERIT |          : project submit type
             FAST_FORWARD_ONLY | MERGE_IF_NECESSARY
             | REBASE_IF_NECESSARY | REBASE_ALWAYS
             | MERGE_ALWAYS | CHERRY_PICK]
             --suggest-parents (-S)                 : suggest parent candidates, if this
                                                      option is used all other options and
                                                      arguments are ignored (default: false)
             --trace                                : enable request tracing (default:
                                                      false)
             --trace-id VAL                         : trace ID (can only be set if --trace
                                                      was set too)
             --use-content-merge                    : allow automatic conflict resolving
                                                      within files
             --use-contributor-agreements (--ca)    : if contributor agreement is required
             --use-signed-off-by (--so)             : if signed-off-by is required

        """
        status, data = self.run_gerrit_command('create-project', project, '--empty-commit', **kwargs)

        return status, data

    def create_branch(self, project, branch, revision='refs/meta/config', **kwargs):
        """
        gerrit create-branch PROJECT NAME REVISION [--] [--help (-h)] [--trace] [--trace-id VAL]

         PROJECT        : name of the project
         NAME           : name of branch to be created
         REVISION       : base revision of the new branch
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('create-branch', project, branch, revision, **kwargs)

        return status, data

    def create_group(self, group, **kwargs):
        """
        gerrit create-group GROUP [--] [--description (-d) DESC] [--group (-g) GROUP] [--help (-h)] [--member (-m) USERNAME] [--owner (-o) GROUP] [--trace] [--trace-id VAL] [--visible-to-all]

         GROUP                   : name of group to be created
         --                      : end of options (default: false)
         --description (-d) DESC : description of group (default: )
         --group (-g) GROUP      : initial set of groups to be included in the group
         --help (-h)             : display this help text
         --member (-m) USERNAME  : initial set of users to become members of the group
         --owner (-o) GROUP      : owning group, if not specified the group will be
                                   self-owning
         --trace                 : enable request tracing (default: false)
         --trace-id VAL          : trace ID (can only be set if --trace was set too)
         --visible-to-all        : to make the group visible to all registered users
                                   (default: false)

        """

        status, data = self.run_gerrit_command('create-group', group, **kwargs)

        return status, data

    def flush_caches(self, **kwargs):
        """
        gerrit flush-caches [--] [--all] [--cache NAME] [--help (-h)] [--list] [--trace] [--trace-id VAL]

         --             : end of options (default: false)
         --all          : flush all caches (default: false)
         --cache NAME   : flush named cache
         --help (-h)    : display this help text
         --list         : list available caches (default: false)
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('flush-caches', **kwargs)

        return status, data

    def gc(self, projects, **kwargs):
        """
        gerrit gc [NAME ...] [--] [--aggressive] [--all] [--help (-h)] [--show-progress] [--trace] [--trace-id VAL]

         NAME            : projects for which the Git garbage collection should be run
         --              : end of options (default: false)
         --aggressive    : run aggressive garbage collection (default: false)
         --all           : runs the Git garbage collection for all projects (default:
                           false)
         --help (-h)     : display this help text
         --show-progress : progress information is shown (default: false)
         --trace         : enable request tracing (default: false)
         --trace-id VAL  : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('gc', projects, **kwargs)

        return status, data

    def ls_groups(self, **kwargs):
        """
        gerrit ls-groups [--] [--help (-h)] [--trace] [--trace-id VAL] [--verbose (-v)] [-o [MEMBERS | INCLUDES]] [--visible-to-all] [--limit (-n) CNT] [--suggest (-s) VAL] [--start (-S) CNT] [--project (-p) PROJECT] [--group (-g) GROUP] [--owned-by VAL] [--user (-u) EMAIL] [--owned] [--match (-m) MATCH] [--regex (-r) REGEX] [-O VAL] [--query (-q) GROUP]

         --                      : end of options (default: false)
         --help (-h)             : display this help text
         --trace                 : enable request tracing (default: false)
         --trace-id VAL          : trace ID (can only be set if --trace was set too)
         --verbose (-v)          : verbose output format with tab-separated columns for
                                   the group name, UUID, description, owner group name,
                                   owner group UUID, and whether the group is visible
                                   to all (default: false)
         -o [MEMBERS | INCLUDES] : Output options per group
         --visible-to-all        : to list only groups that are visible to all
                                   registered users
         --limit (-n) CNT        : maximum number of groups to list
         --suggest (-s) VAL      : to get a suggestion of groups
         --start (-S) CNT        : number of groups to skip
         --project (-p) PROJECT  : projects for which the groups should be listed
         --group (-g) GROUP      : group to inspect
         --owned-by VAL          : list groups owned by the given group uuid
         --user (-u) EMAIL       : user for which the groups should be listed
         --owned                 : to list only groups that are owned by the specified
                                   user or by the calling user if no user was specifed
         --match (-m) MATCH      : match group substring
         --regex (-r) REGEX      : match group regex
         -O VAL                  : Output option flags, in hexreturn status, data
         --query (-q) GROUP      : group to inspect (deprecated: use --group/-g instead)

        """
        status, data = self.run_gerrit_command('ls-groups', **kwargs)

        return data.split('\n') if status == 0 else []

    def ls_members(self, group, **kwargs):
        """
        gerrit ls-members GROUPNAME [--help (-h)] [--recursive]

         GROUPNAME   : the name of the group
         --help (-h) : display this help text
         --recursive : to resolve included groups recursively (default: false)

        """
        members = []
        status, data = self.run_gerrit_command('ls-members', group, **kwargs)
        if status == 0:
            member_list = data.split('\n')[1:]
            for member_str in member_list:
                user_list = member_str.split('\t')
                user = User()
                user._account_id = user_list[0]
                user.username = user_list[1]
                user.name = user_list[2]
                user.email = user_list[3]
                members.append(user)

        return members

    def ls_projects(self, **kwargs):
        """
        gerrit ls-projects [--] [--help (-h)] [--trace] [--trace-id VAL] [--state (-s) [ACTIVE | READ_ONLY | HIDDEN]] [--limit (-n) CNT] [--start (-S) CNT] [--match (-m) MATCH] [-r REGEX] [--description (-d)] [--prefix (-p) PREFIX] [--tree (-t)] [--show-branch (-b) VAL] [--type [CODE | PARENT_CANDIDATES | PERMISSIONS | ALL]] [--has-acl-for GROUP] [--all] [--format [TEXT | JSON | JSON_COMPACT]]

         --                                     : end of options (default: false)
         --help (-h)                            : display this help text
         --trace                                : enable request tracing (default:
                                                  false)
         --trace-id VAL                         : trace ID (can only be set if --trace
                                                  was set too)
         --state (-s) [ACTIVE | READ_ONLY |     : filter by project state
         HIDDEN]
         --limit (-n) CNT                       : maximum number of projects to list
         --start (-S) CNT                       : number of projects to skip
         --match (-m) MATCH                     : match project substring
         -r REGEX                               : match project regex
         --description (-d)                     : include description of project in list
         --prefix (-p) PREFIX                   : match project prefix
         --tree (-t)                            : displays project inheritance in a
                                                  tree-like format
                                                  this option does not work together
                                                  with the show-branch option
         --show-branch (-b) VAL                 : displays the sha of each project in
                                                  the specified branch
         --type [CODE | PARENT_CANDIDATES |     : type of project
         PERMISSIONS | ALL]
         --has-acl-for GROUP                    : displays only projects on which
                                                  access rights for this group are
                                                  directly assigned
         --all                                  : display all projects that are
                                                  accessible by the calling user
         --format [TEXT | JSON | JSON_COMPACT]  : (deprecated) output format (default:
                                                  TEXT)

        """

        status, data = self.run_gerrit_command('ls-projects', **kwargs)

        return data.split('\n') if status == 0 else []

    def ls_user_refs(self, **kwargs):
        """
        gerrit ls-user-refs [--] [--help (-h)] [--only-refs-heads] --project (-p) PROJECT [--trace] [--trace-id VAL] --user (-u) USER

         --                     : end of options (default: false)
         --help (-h)            : display this help text
         --only-refs-heads      : list only refs under refs/heads (default: false)
         --project (-p) PROJECT : project for which the refs should be listed
         --trace                : enable request tracing (default: false)
         --trace-id VAL         : trace ID (can only be set if --trace was set too)
         --user (-u) USER       : user for which the groups should be listed

        """
        status, data = self.run_gerrit_command('ls-user-refs', **kwargs)

        return status, data

    def query(self, query, **kwargs):
        """
        gerrit query QUERY ... [--] [--all-approvals] [--all-reviewers] [--comments] [--commit-message] [--current-patch-set] [--dependencies] [--files] [--format [TEXT | JSON]] [--help (-h)] [--patch-sets] [--start (-S) N] [--submit-records] [--trace] [--trace-id VAL]

         QUERY                  : Query to execute
         --                     : end of options (default: false)
         --all-approvals        : Include information about all patch sets and approvals
         --all-reviewers        : Include all reviewers
         --comments             : Include patch set and inline comments
         --commit-message       : Include the full commit message for a change
         --current-patch-set    : Include information about current patch set
         --dependencies         : Include depends-on and needed-by information
         --files                : Include file list on patch sets
         --format [TEXT | JSON] : Output display format
         --help (-h)            : display this help text
         --patch-sets           : Include information about all patch sets
         --start (-S) N         : Number of changes to skip
         --submit-records       : Include submit and label status
         --trace                : enable request tracing (default: false)
         --trace-id VAL         : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('query', query, **kwargs)

        return status, data

    def receive_pack(self, project, **kwargs):
        """
        gerrit receive-pack PROJECT.git [--] [--cc EMAIL] [--help (-h)] [--reviewer (--re) EMAIL]

         PROJECT.git             : project name
         --                      : end of options (default: false)
         --cc EMAIL              : CC user on change(s)
         --help (-h)             : display this help text
         --reviewer (--re) EMAIL : request reviewer for change(s)

        """
        status, data = self.run_gerrit_command('receive-pack', project, **kwargs)

        return status, data

    def reload_config(self, **kwargs):
        """
        gerrit reload-config [--] [--help (-h)] [--trace] [--trace-id VAL]

         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """

        status, data = self.run_gerrit_command('reload-config', **kwargs)

        return status, data

    def rename_group(self, group, newname, **kwargs):
        """
        gerrit rename-group GROUP NEWNAME [--] [--help (-h)] [--trace] [--trace-id VAL]

         GROUP          : name of the group to be renamed
         NEWNAME        : new name of the group
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('rename-group', group, newname, **kwargs)

        return status, data

    def review(self, commits, **kwargs):
        """
        gerrit review {COMMIT | CHANGE,PATCHSET} ... [--] [--abandon] [--branch (-b) VAL] [--help (-h)] [--json (-j)] [--label (-l) LABEL=VALUE] [--message (-m) MESSAGE] [--move BRANCH] [--notify (-n) [NONE | OWNER | OWNER_REVIEWERS | ALL]] [--project (-p) PROJECT] [--rebase] [--restore] [--submit (-s)] [--tag (-t) TAG] [--trace] [--trace-id VAL] [--code-review N]

         {COMMIT | CHANGE,PATCHSET}             : list of commits or patch sets to
                                                  review
         --                                     : end of options (default: false)
         --abandon                              : abandon the specified change(s)
                                                  (default: false)
         --branch (-b) VAL                      : branch containing the specified patch
                                                  set(s)
         --help (-h)                            : display this help text
         --json (-j)                            : read review input json from stdin
                                                  (default: false)
         --label (-l) LABEL=VALUE               : custom label(s) to assign
         --message (-m) MESSAGE                 : cover message to publish on change(s)
         --move BRANCH                          : move the specified change(s)
         --notify (-n) [NONE | OWNER |          : Who to send email notifications to
         OWNER_REVIEWERS | ALL]                   after the review is stored.
         --project (-p) PROJECT                 : project containing the specified
                                                  patch set(s)
         --rebase                               : rebase the specified change(s)
                                                  (default: false)
         --restore                              : restore the specified abandoned
                                                  change(s) (default: false)
         --submit (-s)                          : submit the specified patch set(s)
                                                  (default: false)
         --tag (-t) TAG                         : applies a tag to the given review
         --trace                                : enable request tracing (default:
                                                  false)
         --trace-id VAL                         : trace ID (can only be set if --trace
                                                  was set too)
         --code-review N                        : score for Code-Review
                                                  -2 This shall not be merged
                                                  -1 I would prefer this is not merged
                                                  as is
                                                   0 No score
                                                  +1 Looks good to me, but someone else
                                                  must approve
                                                  +2 Looks good to me, approved
        """
        status, data = self.run_gerrit_command('review', commits, **kwargs)

        return status, data

    def set_account(self, user, **kwargs):
        """
        gerrit set-account USER [--] [--active] [--add-email EMAIL] [--add-ssh-key -|KEY] [--clear-http-password] [--delete-email EMAIL] [--delete-ssh-key -|KEY] [--full-name NAME] [--generate-http-password] [--help (-h)] [--http-password PASSWORD] [--inactive] [--preferred-email EMAIL] [--trace] [--trace-id VAL]

         USER                     : full name, email-address, ssh username or account id
         --                       : end of options (default: false)
         --active                 : set account's state to active (default: false)
         --add-email EMAIL        : email addresses to add to the account
         --add-ssh-key -|KEY      : public keys to add to the account
         --clear-http-password    : clear HTTP password for the account (default: false)
         --delete-email EMAIL     : email addresses to delete from the account
         --delete-ssh-key -|KEY   : public keys to delete from the account
         --full-name NAME         : display name of the account
         --generate-http-password : generate a new HTTP password for the account
                                    (default: false)
         --help (-h)              : display this help text
         --http-password PASSWORD : password for HTTP authentication for the account
         --inactive               : set account's state to inactive (default: false)
         --preferred-email EMAIL  : a registered email address from the account
         --trace                  : enable request tracing (default: false)
         --trace-id VAL           : trace ID (can only be set if --trace was set too)
        """

        status, data = self.run_gerrit_command('set-account', user, **kwargs)

        return status, data

    def set_head(self, project, **kwargs):
        """
        gerrit set-head NAME [--] [--help (-h)] --new-head REF [--trace] [--trace-id VAL]

         NAME           : name of the project
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --new-head REF : new HEAD reference
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('set-head', project, **kwargs)

        return status, data

    def set_members(self, groups, **kwargs):
        """
        gerrit set-members GROUP ... [--] [--add (-a) USER] [--exclude (-e) GROUP] [--help (-h)] [--include (-i) GROUP] [--remove (-r) USER] [--trace] [--trace-id VAL]

         GROUP                : groups to modify
         --                   : end of options (default: false)
         --add (-a) USER      : users that should be added as group member
         --exclude (-e) GROUP : group that should be excluded from the group
         --help (-h)          : display this help text
         --include (-i) GROUP : group that should be included as group member
         --remove (-r) USER   : users that should be removed from the group
         --trace              : enable request tracing (default: false)
         --trace-id VAL       : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('set-members', groups, **kwargs)

        return status, data

    def set_project(self, project, **kwargs):
        """
        gerrit set-project NAME [--] [--change-id [TRUE | FALSE | INHERIT]] [--content-merge [TRUE | FALSE | INHERIT]] [--contributor-agreements [TRUE | FALSE | INHERIT]] [--description (-d) DESCRIPTION] [--help (-h)] [--max-object-size-limit VAL] [--no-change-id (--nid)] [--no-content-merge] [--no-contributor-agreements (--nca)] [--no-signed-off-by (--nso)] [--project-state (--ps) [ACTIVE | READ_ONLY | HIDDEN]] [--require-change-id (--id)] [--signed-off-by [TRUE | FALSE | INHERIT]] [--submit-type (-t) [INHERIT | FAST_FORWARD_ONLY | MERGE_IF_NECESSARY | REBASE_IF_NECESSARY | REBASE_ALWAYS | MERGE_ALWAYS | CHERRY_PICK]] [--trace] [--trace-id VAL] [--use-content-merge] [--use-contributor-agreements (--ca)] [--use-signed-off-by (--so)]

         NAME                                   : name of the project
         --                                     : end of options (default: false)
         --change-id [TRUE | FALSE | INHERIT]   : if change-id is required
         --content-merge [TRUE | FALSE |        : allow automatic conflict resolving
         INHERIT]                                 within files
         --contributor-agreements [TRUE |       : if contributor agreement is required
         FALSE | INHERIT]
         --description (-d) DESCRIPTION         : description of project
         --help (-h)                            : display this help text
         --max-object-size-limit VAL            : max Git object size for this project
         --no-change-id (--nid)                 : if change-id is not required
         --no-content-merge                     : don't allow automatic conflict
                                                  resolving within files
         --no-contributor-agreements (--nca)    : if contributor agreement is not
                                                  required
         --no-signed-off-by (--nso)             : if signed-off-by is not required
         --project-state (--ps) [ACTIVE |       : project's visibility state
         READ_ONLY | HIDDEN]
         --require-change-id (--id)             : if change-id is required
         --signed-off-by [TRUE | FALSE |        : if signed-off-by is required
         INHERIT]
         --submit-type (-t) [INHERIT |          : project submit type
         FAST_FORWARD_ONLY | MERGE_IF_NECESSARY   (default: MERGE_IF_NECESSARY)
         | REBASE_IF_NECESSARY | REBASE_ALWAYS
         | MERGE_ALWAYS | CHERRY_PICK]
         --trace                                : enable request tracing (default:
                                                  false)
         --trace-id VAL                         : trace ID (can only be set if --trace
                                                  was set too)
         --use-content-merge                    : allow automatic conflict resolving
                                                  within files
         --use-contributor-agreements (--ca)    : if contributor agreement is required
         --use-signed-off-by (--so)             : if signed-off-by is required
        """
        status, data = self.run_gerrit_command('set-project', project, **kwargs)

        return status, data

    def set_project_parent(self, project, **kwargs):
        """
        gerrit set-project-parent [NAME ...] [--] [--children-of NAME] [--exclude NAME] [--help (-h)] [--parent (-p) NAME] [--trace] [--trace-id VAL]

         NAME               : projects to modify
         --                 : end of options (default: false)
         --children-of NAME : parent project for which the child projects should be
                              reparented
         --exclude NAME     : child project of old parent project which should not be
                              reparented
         --help (-h)        : display this help text
         --parent (-p) NAME : new parent project
         --trace            : enable request tracing (default: false)
         --trace-id VAL     : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('set-project-parent', project, **kwargs)

        return status, data

    def set_reviewers(self, changes, **kwargs):
        """
        gerrit set-reviewers CHANGE ... [--] [--add (-a) REVIEWER] [--help (-h)] [--project (-p) PROJECT] [--remove (-r) REVIEWER] [--trace] [--trace-id VAL]

         CHANGE                 : changes to modify
         --                     : end of options (default: false)
         --add (-a) REVIEWER    : user or group that should be added as reviewer
         --help (-h)            : display this help text
         --project (-p) PROJECT : project containing the change
         --remove (-r) REVIEWER : user that should be removed from the reviewer list
         --trace                : enable request tracing (default: false)
         --trace-id VAL         : trace ID (can only be set if --trace was set too)

        """
        status, data = self.run_gerrit_command('set-reviewers', changes, **kwargs)

        return status, data

    def show_caches(self, **kwargs):
        """
        gerrit show-caches [--] [--gc] [--help (-h)] [--show-jvm] [--show-threads] [--trace] [--trace-id VAL] [--width (-w) COLS]

         --                : end of options (default: false)
         --gc              : perform Java GC before printing memory stats (default:
                             false)
         --help (-h)       : display this help text
         --show-jvm        : show details about the JVM (default: false)
         --show-threads    : show detailed thread counts (default: false)
         --trace           : enable request tracing (default: false)
         --trace-id VAL    : trace ID (can only be set if --trace was set too)
         --width (-w) COLS : width of output table (default: 80)

        """
        status, data = self.run_gerrit_command('show-caches', **kwargs)

        return status, data

    def show_connections(self, **kwargs):
        """
        gerrit show-connections [--] [--help (-h)] [--numeric (-n)] [--trace] [--trace-id VAL] [--wide (-w)]

         --             : end of options (default: false)
         --help (-h)    : display this help text
         --numeric (-n) : don't resolve names (default: false)
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)
         --wide (-w)    : display without line width truncation (default: false)

        """
        status, data = self.run_gerrit_command('show-connections', **kwargs)

        return status, data

    def show_queue(self, **kwargs):
        """
        gerrit show-queue [--] [--by-queue (-q)] [--help (-h)] [--trace] [--trace-id VAL] [--wide (-w)]

         --              : end of options (default: false)
         --by-queue (-q) : group tasks by queue and print queue info (default: false)
         --help (-h)     : display this help text
         --trace         : enable request tracing (default: false)
         --trace-id VAL  : trace ID (can only be set if --trace was set too)
         --wide (-w)     : display without line width truncation (default: false)

        """
        status, data = self.run_gerrit_command('show-queue', **kwargs)

        return status, data

    def stream_events(self, **kwargs):
        """
        gerrit stream-events [--] [--help (-h)] [--subscribe (-s) SUBSCRIBE]

         --                         : end of options (default: false)
         --help (-h)                : display this help text
         --subscribe (-s) SUBSCRIBE : subscribe to specific stream-events

        """
        status, data = self.run_gerrit_command('stream-events', **kwargs)

        return status, data

    def version(self, **kwargs):
        """
        gerrit version [--] [--help (-h)] [--trace] [--trace-id VAL]

         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)
        """
        status, data = self.run_gerrit_command('version', **kwargs)

        return data if status == 0 else None


if __name__ == '__main__':
    server = GerritSSHCommands('gerrit56')
    # server.create_project('oppo')
