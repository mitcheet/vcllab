# Create your views here.
# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from lab.models import computerlab
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.contrib.auth import logout
from django.contrib.auth.models import User
import os
import time
import boto
import boto.manage.cmdshell
import boto.manage.server

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/lab')
    
@login_required(login_url='/accounts/login/')
def index(request):
    myuser = request.user
    action = 'Do Nothing'
    if 'iid' in request.POST:
        iid = request.POST['iid']
	if 'action' in request.POST:
            action = request.POST['action']
            if action == 'Start Server':
                result = start_instance(iid)
            if action == 'Stop Server':
                result = stop_instance(iid)
            if action == 'Create Server':
        	iitype = request.POST['instance_type']
		result = create_instance(username=myuser.username, instance_type=iitype)
            if action == 'Terminate Server':
                result = terminate_instance(iid)
    list_of_machines = list_instances(username=myuser.username)
    list_of_labs = computerlab.objects.all()
    return render_to_response('lab/index.html', {'list_of_machines':list_of_machines, 'myuser':myuser, 'action': action, 'list_of_labs':list_of_labs}, context_instance=RequestContext(request))

    output =  'Your instance is ready to use!  RDP or SSH to: ',instance.dns_name
        #selected_choice.votes += 1
        #selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
    return HttpResponseRedirect(reverse('lab.index', args=(output,)))

     


###################################################

#code from vcl


def create_instance(ami='ami-456ac22c',
                    instance_type='t1.micro',
                    key_name='aws_vcl_key',
                    key_extension='.pem',
                    key_dir='~/.ssh',
                    group_name='default',
                    ssh_port=22,
                    cidr='0.0.0.0/0',
                    tag='LBSC_670',
                    user_data=None,
                    cmd_shell=True,
                    login_user='ubuntu',
                    ssh_passwd=None,
                    username = 'mitcheet',
                    classcode='LBSC670',
                    azone = 'us-east-1c'):
    """
    Launch an instance and wait for it to start running.
    Returns a tuple consisting of the Instance object and the CmdShell
    object, if request, or None.

    ami        The ID of the Amazon Machine Image that this instance will
               be based on.  Default is a 64-bit Amazon Linux EBS image.

    instance_type The type of the instance.

    key_name   The name of the SSH Key used for logging into the instance.
               It will be created if it does not exist.

    key_extension The file extension for SSH private key files.
    
    key_dir    The path to the directory containing SSH private keys.
               This is usually ~/.ssh.

    group_name The name of the security group used to control access
               to the instance.  It will be created if it does not exist.

    ssh_port   The port number you want to use for SSH access (default 22).

    cidr       The CIDR block used to limit access to your instance.

    tag        A name that will be used to tag the instance so we can
               easily find it later.

    user_data  Data that will be passed to the newly started
               instance at launch and will be accessible via
               the metadata service running at http://169.254.169.254.

    cmd_shell  If true, a boto CmdShell object will be created and returned.
               This allows programmatic SSH access to the new instance.

    login_user The user name used when SSH'ing into new instance.  The
               default is 'ec2-user'

    ssh_passwd The password for your SSH key if it is encrypted with a
               passphrase.
    """
    cmd = None
    
    # Create a connection to EC2 service.
    # You can pass credentials in to the connect_ec2 method explicitly
    # or you can use the default credentials in your ~/.boto config file
    # as we are doing here.
    ec2 = boto.connect_ec2()
    
    # Check to see if specified keypair already exists.
    # If we get an InvalidKeyPair.NotFound error back from EC2,
    # it means that it doesn't exist and we need to create it.
    try:
        key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidKeyPair.NotFound':
            print 'Creating keypair: %s' % key_name
            # Create an SSH key to use when logging into instances.
            key = ec2.create_key_pair(key_name)
            
            # AWS will store the public key but the private key is
            # generated and returned and needs to be stored locally.
            # The save method will also chmod the file to protect
            # your private key.
            key.save(key_dir)
        else:
            raise

    # Check to see if specified security group already exists.
    # If we get an InvalidGroup.NotFound error back from EC2,
    # it means that it doesn't exist and we need to create it.
    try:
        group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidGroup.NotFound':
            print 'Creating Security Group: %s' % group_name
            # Create a security group to control access to instance via SSH.
            group = ec2.create_security_group(group_name,
                                              'A group that allows SSH access')
        else:
            raise

    # Add a rule to the security group to authorize SSH traffic
    # on the specified port.
    try:
        group.authorize('tcp', ssh_port, ssh_port, cidr)
    except ec2.ResponseError, e:
        if e.code == 'InvalidPermission.Duplicate':
            print 'Security Group: %s already authorized' % group_name
        else:
            raise

	#find the volume for the user and class in question
	#volumes = ec2.get_all_volumes(filters={'tag-value': username, 'tag-value':classcode})
	#Attach the volume to the server
	#result = volumes.attach(instance, '/dev/sdf')
	#define user data to mount the volume
    # Now start up the instance.  The run_instances method
    # has many, many parameters but these are all we need
    # for now.
    reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data,
                                    placement=azone)

    # Find the actual Instance object inside the Reservation object
    # returned by EC2.

    instance = reservation.instances[0]
    machinename = classcode + "--" + username
    #Add user tags to it
    instance.add_tag('username', username)
    instance.add_tag('classcode', classcode)
    instance.add_tag('Name', machinename)

    # The instance has been launched but it's not yet up and
    # running.  Let's wait for its state to change to 'running'.

    print 'waiting for instance'
    while instance.state != 'running':
        print '.'
        time.sleep(5)
        instance.update()
    return 'Your instance has been created and is running at', instance.dns_name, '  Please use NX Viewer or remote desktop to connect.'


	
def start_instance(iid):         
    ec2 = boto.connect_ec2()
    reservations = ec2.get_all_instances(filters={'instance-id': iid})
    instance = reservations[0].instances[0]
    iid = [instance.id]
    instance_state = ec2.start_instances(iid)
    while instance.state != 'running':
        print '.'
        time.sleep(5)
        instance.update()
	
def stop_instance(iid):
    ec2 = boto.connect_ec2()
    reservations = ec2.get_all_instances(filters={'instance-id': iid})
    instance = reservations[0].instances[0]
    iid = [instance.id]
    instance_state = ec2.stop_instances(iid)
    while instance.state != 'stopped':
        print '.'
        time.sleep(5)
        instance.update()

def terminate_instance(iid):
    ec2 = boto.connect_ec2()
    reservations = ec2.get_all_instances(filters={'instance-id': iid})
    instance = reservations[0].instances[0]
    iid = [instance.id]
    instance_state = ec2.terminate_instances(iid)
    while instance.state != 'stopped':
        print '.'
        time.sleep(5)
        instance.update()
		
def list_instances(ami='ami-456ac22c',
                   instance_type='t1.micro',
                   key_name='aws_vcl_key',
                   key_extension='.pem',
                   key_dir='~/.ssh',
                   group_name='default',
                   ssh_port=22,
                   cidr='0.0.0.0/0',
                   tag='LBSC_670',
                   user_data=None,
                   cmd_shell=True,
                   login_user='ubuntu',
                   ssh_passwd=None,
                   username = 'mitcheet',
                   classcode='LBSC670',
                   azone = 'us-east-1c'):         
		ec2 = boto.connect_ec2()
		reservations = ec2.get_all_instances(filters={'tag-value': username})
		machines = {}
		for reservation in reservations:
			instance = reservation.instances[0]
			instance_tags = instance.tags
			if instance_tags[u'Name']:	
				instance_name = instance_tags[u'Name']	
			else:
				instance_name = "Lab machine"
			if instance.state != 'terminated':
				machines[instance.id] = {'instance_name': instance_name,'instance_id': instance.id, 'instance_state': instance.state, 'ami_id': instance.image_id, 'public_dns': instance.public_dns_name}

		return machines
