env = {}

env['user'] = 'root'
env['password'] = 'Kanishq1210%40MySQL'

env['db_credentials'] = "{}:{}".format(env['user'], env['password']) if env['password'] else env['user']