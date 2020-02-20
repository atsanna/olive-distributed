import Pyro4.core
import socket


class Safe(object):
    @Pyro4.expose
    def echo(self, message):
        print("got message:", message)
        return "hi!"


Pyro4.config.SSL = True
Pyro4.config.SSL_REQUIRECLIENTCERT = True   # enable 2-way ssl
Pyro4.config.SSL_SERVERCERT = "certs/node_cert.pem"
Pyro4.config.SSL_SERVERKEY = "certs/node_key.pem"
Pyro4.config.SSL_CACERTS = "certs/master_cert.pem"    # to make ssl accept the self-signed master cert
print("SSL enabled (2-way).")


class CertValidatingDaemon(Pyro4.core.Daemon):
    def validateHandshake(self, conn, data):
        cert = conn.getpeercert()
        if not cert:
            raise Pyro4.errors.CommunicationError("client cert missing")
        '''
        if cert["serialNumber"] != "9BFD9872D96F066C":
            raise Pyro4.errors.CommunicationError("cert serial number incorrect")
        issuer = dict(p[0] for p in cert["issuer"])
        subject = dict(p[0] for p in cert["subject"])
        if issuer["organizationName"] != "Razorvine.net":
            # issuer is not often relevant I guess, but just to show that you have the data
            raise Pyro4.errors.CommunicationError("cert not issued by Razorvine.net")
        if subject["countryName"] != "NL":
            raise Pyro4.errors.CommunicationError("cert not for country NL")
        if subject["organizationName"] != "Razorvine.net":
            raise Pyro4.errors.CommunicationError("cert not for Razorvine.net")
        print("(SSL client cert is ok: serial={ser}, subject={subj})"
              .format(ser=cert["serialNumber"], subj=subject["organizationName"]))
        '''
        return super(CertValidatingDaemon, self).validateHandshake(conn, data)


d = CertValidatingDaemon(host=socket.gethostname(), port=9090)
uri = d.register(Safe, "NodeService")

print("server uri:", uri)
d.requestLoop()
