from fabric.api import env, run, local
from time import sleep

env.shell = "/bin/sh -c"
#env.user = "m2"

def _make_env(prod=None, app_num=6, db_num=None, lb_num=None, util=True):
    hosts = []
    #setup apps
    hosts.extend(["app%d.prod%s"%(i,prod) for i in range(1,app_num+1)])
    #setup db
    if db_num:
        hosts.extend(["db%d.prod%s"%(i,prod) for i in range(1,db_num+1)])
    #setub lb
    if lb_num:
        hosts.extend(["lb%d.prod%s"%(i,prod) for i in range(1,lb_num+1)])
    #setup util
    if util:
        hosts.append("util.prod%s"%prod)

    return hosts

# define central and edge supergroups
env.roledefs['centrals'] = []
env.roledefs['edges'] = []

# 6-app centrals
for prod in [3, 4, 5, 6, 7, 9, 12, 16, 'xx', 'yy']:
    env.roledefs['%s'%prod] = _make_env(prod=prod,db_num=2)
    env.roledefs['centrals'].extend(env.roledefs['%s'%prod])

# 6-app edge
for prod in [14, 15, 18, 20]:
    env.roledefs['%s'%prod] = _make_env(prod=prod)
    env.roledefs['edges'].extend(env.roledefs['%s'%prod])

# 12-app edge
for prod in [17, 19]:
    env.roledefs['%s'%prod] = _make_env(prod=prod, app_num=12)
    env.roledefs['edges'].extend(env.roledefs['%s'%prod])

###### tasks below! ###### 

def only(key=''):
    """Filters hosts by given key.  Use as first task, e.g.: "only:app" """
    env.hosts = [host for host in env.all_hosts if key in host]
    env.roles = []

def exclude(key=''):
    """Filters hosts by given key.  Use as first task, e.g.: "exclude:app" """
    env.hosts = [host for host in env.all_hosts if key not in host]
    env.roles = []

def host_debug():
    print '%s'%env.host

def ver():
    run('ver')

def slow_bounce_apps(delay=3):
    delay = float(delay)
    run('bounce -a')
    sleep(delay)

def get_latest_release(app='central'):
    run('ls -dt ~/work/releases/*%s-* | head -1'%app)

def verify_ver():
    x = raw_input("run ver on %s? [y/n]"%env.host)
    if x == 'y':
        run('ver')

def pause(message="Press enter to continue..."):
    """Insert a pause in a string of tasks. This pauses once for all hosts"""
    # This is a global pause, so we only want to run once per group of hosts
    if env.hosts.index(env.host) == 0:
        raw_input(message)

def test():
    success_threshold = 3
    done = False
    output = ''
    last_output = output
    success_count = 0

    while not done:
        output = run('tail -1 /tmp/logfile')
        if output == last_output:
            print 'output the same, I will wait'
        else:
            #print 'output is %s'%output
            if output.find('200') != -1:
                success_count += 1
            print "success count: %s"%success_count
            if success_count >= success_threshold:
                print "Success threshold reached."
                done = True

        sleep(5)
        last_output = output


    #run('tail -f /tmp/logfile')
    #output = run('tail -f /tmp/logfile')
    #print "This is the output: \n %s"%(output)


def check_staging_edge(verbose=False):
    output = local('echo foo for %s'%env.host)
    if verbose:
        print 'yehaa'
    else:
        print output
