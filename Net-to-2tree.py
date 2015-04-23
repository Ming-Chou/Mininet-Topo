from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import lg
from mininet.node import Node
from mininet.topolib import TreeNet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.net import Mininet


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

    Host1 = net.addHost('h1')
    Host2 = net.addHost('h2')
    Host3 = net.addHost('h3')
    Host4 = net.addHost('h4')
    Host5 = net.addHost('h5')
    Host6 = net.addHost('h6')
    Host7 = net.addHost('h7')
    Host8 = net.addHost('h8')
    Host9 = net.addHost('h9')
    Host10 = net.addHost('h10')
    Host11 = net.addHost('h11')
    Host12 = net.addHost('h12')
    Host13 = net.addHost('h13')
    Host14 = net.addHost('h14')
    Host15 = net.addHost('h15')
    Host16 =  net.addHost('h16')

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
    net.addLink(SLLL3,Host1)
    net.addLink(SLLL3,Host2)
    net.addLink(SLLR3,Host3)
    net.addLink(SLLR3,Host4)
    net.addLink(SLRL3,Host5)
    net.addLink(SLRL3,Host6)
    net.addLink(SLRR3,Host7)
    net.addLink(SLRR3,Host8)
    net.addLink(SRLL3,Host9)
    net.addLink(SRLL3,Host10)
    net.addLink(SRLR3,Host11)
    net.addLink(SRLR3,Host12)
    net.addLink(SRRL3,Host13)
    net.addLink(SRRL3,Host14)
    net.addLink(SRRR3,Host15)
    net.addLink(SRRR3,Host16)

    rootnode = connectToInternet( net )
    print "*** Hosts are running and should have internet connectivity"
    print "*** Type 'exit' or control-D to shut down network"
    CLI( net )
    stopNAT( rootnode )
    net.stop()
