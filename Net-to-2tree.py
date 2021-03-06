"""
Host1 & Host16 are outside host.
Host1 IP : 10.0.0.1
Host5 IP : 10.0.0.5
Host12 IP : 10.0.0.12
Host16 IP : 10.0.0.16
Netmask : 255.0.0.0
Gateway : 10.0.0.254
"""

import re
import sys

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import lg, setLogLevel, info, error
from mininet.node import Node
from mininet.topolib import TreeNet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.node import Node
from mininet.net import Mininet
from mininet.link import Intf
from mininet.util import quietRun


def startNAT( root, inetIntf='eth0', subnet='10.0/8' ):
    """Start NAT/forwarding between Mininet and external network
    root: node to access iptables from
    inetIntf: interface for internet access
    subnet: Mininet subnet (default 10.0/8)="""

    # Identify the interface connecting to the mininet network
    localIntf = root.defaultIntf()

    # Flush any currently active rules
    root.cmd( 'iptables -F' )
    root.cmd( 'iptables -t nat -F' )

    # Create default entries for unmatched traffic
    root.cmd( 'iptables -P INPUT ACCEPT' )
    root.cmd( 'iptables -P OUTPUT ACCEPT' )
    root.cmd( 'iptables -P FORWARD DROP' )

    # Configure NAT
    root.cmd( 'iptables -I FORWARD -i', localIntf, '-d', subnet, '-j DROP' )
    root.cmd( 'iptables -A FORWARD -i', localIntf, '-s', subnet, '-j ACCEPT' )
    root.cmd( 'iptables -A FORWARD -i', inetIntf, '-d', subnet, '-j ACCEPT' )
    root.cmd( 'iptables -t nat -A POSTROUTING -o ', inetIntf, '-j MASQUERADE' )

    # Instruct the kernel to perform forwarding
    root.cmd( 'sysctl net.ipv4.ip_forward=1' )

def stopNAT( root ):
    """Stop NAT/forwarding between Mininet and external network"""
    # Flush any currently active rules
    root.cmd( 'iptables -F' )
    root.cmd( 'iptables -t nat -F' )

    # Instruct the kernel to stop forwarding
    root.cmd( 'sysctl net.ipv4.ip_forward=0' )

def fixNetworkManager( root, intf ):
    """Prevent network-manager from messing with our interface,
       by specifying manual configuration in /etc/network/interfaces
       root: a node in the root namespace (for running commands)
       intf: interface name"""
    cfile = '/etc/network/interfaces'
    line = '\niface %s inet manual\n' % intf
    config = open( cfile ).read()
    if line not in config:
        print '*** Adding', line.strip(), 'to', cfile
        with open( cfile, 'a' ) as f:
            f.write( line )
        # Probably need to restart network-manager to be safe -
        # hopefully this won't disconnect you
        root.cmd( 'service network-manager restart' )

def connectToInternet( network, switch='s1', rootip='10.254', subnet='10.0/8'):
    """Connect the network to the internet
       switch: switch to connect to root namespace
       rootip: address for interface in root namespace
       subnet: Mininet subnet"""
    switch = network.get( switch )
    prefixLen = subnet.split( '/' )[ 1 ]

    # Create a node in root namespace
    root = Node( 'root', inNamespace=False )

    # Prevent network-manager from interfering with our interface
    fixNetworkManager( root, 'root-eth0' )

    # Create link between root NS and switch
    link = network.addLink( root, switch )
    link.intf1.setIP( rootip, prefixLen )

    # Start network that now includes link to root namespace
    network.start()

    # Start NAT and establish forwarding
    startNAT( root )

    # Establish routes from end hosts
    for host in network.hosts:
        host.cmd( 'ip route flush root 0/0' )
        host.cmd( 'route add -net', subnet, 'dev', host.defaultIntf() )
        host.cmd( 'route add default gw', rootip )

    return root

def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    if ( ' %s:' % intf ) not in quietRun( 'ip link show' ):
        error( 'Error:', intf, 'does not exist!\n' )
        exit( 1 )
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', quietRun( 'ifconfig ' + intf ) )
    if ips:
        error( 'Error:', intf, 'has an IP address,'
               'and is probably in use!\n' )
        exit( 1 )


if __name__ == "__main__":
    lg.setLogLevel( 'info')
    #net = TreeNet( depth=1, fanout=4 )
    # Configure and start NATted connectivity
    net = Mininet(listenPort = 6633)

    mycontroller = RemoteController("C0",ip = "192.168.176.132")
    net.addController(mycontroller)

    # Add hosts and switches
    S1 = net.addSwitch('s1')
    SL1 = net.addSwitch('s2')
    SR1 = net.addSwitch('s3')
    SLL2 = net.addSwitch('s4')
    SLR2 = net.addSwitch('s5')
    SRL2 = net.addSwitch('s6')
    SRR2 = net.addSwitch('s7')
    SLLL3 = net.addSwitch('s8')
    SLLR3 = net.addSwitch('s9')
    SLRL3 = net.addSwitch('s10')
    SLRR3 = net.addSwitch('s11')
    SRLL3 = net.addSwitch('s12')
    SRLR3 = net.addSwitch('s13')
    SRRL3 = net.addSwitch('s14')
    SRRR3 = net.addSwitch('s15')

    Host2 = net.addHost('h2', ip = "10.0.0.2")
    Host3 = net.addHost('h3', ip = "10.0.0.3")
    Host4 = net.addHost('h4', ip = "10.0.0.4")
    #Host5 = net.addHost('h5', ip = "10.0.0.5") connect to real virtual machine
    Host6 = net.addHost('h6', ip = "10.0.0.6")
    Host7 = net.addHost('h7', ip = "10.0.0.7")
    Host8 = net.addHost('h8', ip = "10.0.0.8")
    Host9 = net.addHost('h9', ip = "10.0.0.9")
    Host10 = net.addHost('h10', ip = "10.0.0.10")
    Host11 = net.addHost('h11', ip = "10.0.0.11")
    #Host12 = net.addHost('h12', ip = "10.0.0.12") connect to real virtual machine
    Host13 = net.addHost('h13', ip = "10.0.0.13")
    Host14 = net.addHost('h14', ip = "10.0.0.14")
    Host15 = net.addHost('h15', ip = "10.0.0.15")


    # Add links
    net.addLink(S1,SL1)
    net.addLink(S1,SR1)
    net.addLink(SL1,SLL2)
    net.addLink(SL1,SLR2)
    net.addLink(SR1,SRL2)
    net.addLink(SR1,SRR2)
    net.addLink(SLL2,SLLL3)
    net.addLink(SLL2,SLLR3)
    net.addLink(SLR2,SLRL3)
    net.addLink(SLR2,SLRR3)
    net.addLink(SRL2,SRLL3)
    net.addLink(SRL2,SRLR3)
    net.addLink(SRR2,SRRL3)
    net.addLink(SRR2,SRRR3)

    net.addLink(SLLL3,Host2)
    net.addLink(SLLR3,Host3)
    net.addLink(SLLR3,Host4)
    #net.addLink(SLRL3,Host5)
    net.addLink(SLRL3,Host6)
    net.addLink(SLRR3,Host7)
    net.addLink(SLRR3,Host8)
    net.addLink(SRLL3,Host9)
    net.addLink(SRLL3,Host10)
    net.addLink(SRLR3,Host11)
    #net.addLink(SRLR3,Host12)
    net.addLink(SRRL3,Host13)
    net.addLink(SRRL3,Host14)
    net.addLink(SRRR3,Host15)

#-------------Add interface for each Virtual Machine---------------#

    intfName1 = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'eth1'
    info( '*** Connecting to hw intf: %s' % intfName1 )

    info( '*** Checking', intfName1, '\n' )
    checkIntf( intfName1 )

    switch1 = SLLL3
    info( '*** Adding hardware interface', intfName1, 'to switch',
          switch1.name, '\n' )
    _intf = Intf( intfName1, node=switch1 )

    info( '*** Note: you may need to reconfigure the interfaces for '
          'the Mininet hosts:\n', net.hosts, '\n' )

#-------------------------------------------------------------------

    intfName2 = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'eth2'
    info( '*** Connecting to hw intf: %s' % intfName2 )

    info( '*** Checking', intfName2, '\n' )
    checkIntf( intfName2 )

    switch2 = SRRR3
    info( '*** Adding hardware interface', intfName2, 'to switch',
          switch2.name, '\n' )
    _intf = Intf( intfName2, node=switch2 )

    info( '*** Note: you may need to reconfigure the interfaces for '
          'the Mininet hosts:\n', net.hosts, '\n' )

#-------------------------------------------------------------------

    intfName3 = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'eth3'
    info( '*** Connecting to hw intf: %s' % intfName3 )

    info( '*** Checking', intfName3, '\n' )
    checkIntf( intfName3 )

    switch3 = SLRL3 #For IP:10.0.0.5
    info( '*** Adding hardware interface', intfName3, 'to switch',
          switch3.name, '\n' )
    _intf = Intf( intfName3, node=switch3 )

    info( '*** Note: you may need to reconfigure the interfaces for '
          'the Mininet hosts:\n', net.hosts, '\n' )

#-------------------------------------------------------------------

    intfName4 = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'eth4'
    info( '*** Connecting to hw intf: %s' % intfName4 )

    info( '*** Checking', intfName4, '\n' )
    checkIntf( intfName4 )

    switch4 = SRLR3 #For IP:10.0.0.12
    info( '*** Adding hardware interface', intfName4, 'to switch',
          switch4.name, '\n' )
    _intf = Intf( intfName4, node=switch4 )

    info( '*** Note: you may need to reconfigure the interfaces for '
          'the Mininet hosts:\n', net.hosts, '\n' )

#-------------------------------------------------------------------

    rootnode = connectToInternet( net )
    print "*** Hosts are running and should have internet connectivity"
    print "*** Type 'exit' or control-D to shut down network"
    CLI( net )
    stopNAT( rootnode )
    net.stop()

