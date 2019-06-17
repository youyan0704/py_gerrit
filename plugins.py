# -*- coding: utf-8 -*-
# @Time    : 19-5-8 下午6:23
# @Author  : allen.you
import subprocess
from .models.plugin import Plugin


class PluginSSHCommands(object):

    def __init__(self, server):
        self.__server = server
        self.__command = 'ssh {} gerrit plugin %s '.format(self.__server)

    def run_command(self, command, *args, **kwargs):
        """
        param: command, gerrit plugin命令
        param: args, gerrit plugin命令必须参数
        param： kwargs, gerrit plugin命令可选参数，注意当参数key存在中划线‘-’时，使用下划线‘_’代替
        """

        commands = self.__command % command
        for a in args:
            commands = commands + '%s ' % a
        for k in kwargs.items():
            commands = commands + '--%s %s ' % (k[0].replace('_', '-'), k[1])
        try:
            status, data = subprocess.getstatusoutput(commands)
        except Exception as err:
            raise Exception('Command execution error: %s' % err)

        return status, data


    def add(self, url, **kwargs):
        """
        gerrit plugin add [-|URL] [-] [--] [--help (-h)] [--name (-n) VAL] [--trace] [--trace-id VAL]

         -|URL           : JAR to load
         --              : end of options (default: false)
         --help (-h)     : display this help text
         --name (-n) VAL : install under name
         --trace         : enable request tracing (default: false)
         --trace-id VAL  : trace ID (can only be set if --trace was set too)

        """
        self.run_command('add', url, **kwargs)

    def enable(self, plugin, **kwargs):
        """
        gerrit plugin enable NAME ... [--] [--help (-h)] [--trace] [--trace-id VAL]

         NAME           : plugin(s) to enable
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        self.run_command('enable', plugin, **kwargs)

    def install(self, url, **kwargs):
        """
        gerrit plugin install [-|URL] [-] [--] [--help (-h)] [--name (-n) VAL] [--trace] [--trace-id VAL]

         -|URL           : JAR to load
         --              : end of options (default: false)
         --help (-h)     : display this help text
         --name (-n) VAL : install under name
         --trace         : enable request tracing (default: false)
         --trace-id VAL  : trace ID (can only be set if --trace was set too)


        """
        self.run_command('install', url, **kwargs)

    def ls(self, **kwargs):
        """
        gerrit plugin ls [--] [--format [TEXT | JSON | JSON_COMPACT]] [--help (-h)] [--trace] [--trace-id VAL] [--limit (-n) CNT] [--start (-S) CNT] [--match (-m) MATCH] [-r REGEX] [--prefix (-p) PREFIX] [--all (-a)]

         --                                    : end of options (default: false)
         --format [TEXT | JSON | JSON_COMPACT] : output format (default: TEXT)
         --help (-h)                           : display this help text
         --trace                               : enable request tracing (default: false)
         --trace-id VAL                        : trace ID (can only be set if --trace
                                                 was set too)
         --limit (-n) CNT                      : maximum number of plugins to list
         --start (-S) CNT                      : number of plugins to skip
         --match (-m) MATCH                    : match plugin substring
         -r REGEX                              : match plugin regex
         --prefix (-p) PREFIX                  : match plugin prefix
         --all (-a)                            : List all plugins, including disabled
                                                 plugins

        """
        plugins = []
        status, data = self.run_command('ls', **kwargs)

        if status != 0:
            raise Exception(data)
        # title = data.split('\n')[0].split()
        data = data.split('\n')[2:]
        for plugin_str in data:
            plugin_data = plugin_str.split()
            plugin = Plugin()
            plugin.id = plugin_data[0]
            plugin.version = plugin_data[1]
            plugin.status = plugin_data[2]
            plugin.filename = plugin_data[3]

            plugins.append(plugin)

        return plugins


    def reload(self, plugin, **kwargs):
        """
        gerrit plugin reload [NAME ...] [--] [--help (-h)] [--trace] [--trace-id VAL]

         NAME           : plugins to reload/restart
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        self.run_command('reload', plugin, **kwargs)

    def remove(self, plugin, **kwargs):
        """
        gerrit plugin remove NAME ... [--] [--help (-h)] [--trace] [--trace-id VAL]

         NAME           : plugin to remove
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        self.run_command('remove', plugin, **kwargs)

    def rm(self, plugin, **kwargs):
        """
        gerrit plugin rm NAME ... [--] [--help (-h)] [--trace] [--trace-id VAL]

         NAME           : plugin to remove
         --             : end of options (default: false)
         --help (-h)    : display this help text
         --trace        : enable request tracing (default: false)
         --trace-id VAL : trace ID (can only be set if --trace was set too)

        """
        self.run_command('rm', plugin, **kwargs)



if __name__ == "__main__":
    plugins = PluginSSHCommands('gerrit56')
    for p in plugins.ls():
        print(p)
