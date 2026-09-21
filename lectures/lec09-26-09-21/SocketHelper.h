

#ifndef __SOCKET_HELPER_H
#define __SOCKET_HELPER_H

#define DEFAULT_LISTEN_BACKLOG      10

// createSocket_TCP_Listen
//
//   A set of functions that assist with creating a TCP socket by iterating through
//   using getaddrinfo (IPv4, IPv6 friendly) and attempting to create a fully-initialized
//   TCP socket that has successfully been transitioned to a listen state whereby the 
//   socket itself can now be used to accept inbound connection requests
//
//   For each of the functions, C-style strings are used for the server and the 
//   port number as appropriate.  If one leaves off the server name (keeps it NULL),
//   that effectively creates a socket that will listen across all relevant IP addresses
//   associated with this particular hosts

/** Create a TCP socket that is listening on the specified port 
 * @param nPort The port to listen on
 * @returns Non-zero socket file descriptor if successful, zero otherwise 
 * */ 
int createSocket_TCP_Listen (uint16_t nPort);

/** Create a TCP socket that is listening on the specified port. 
 * @param pszServer String specifying the hostname / IP address (may be NULL)
 * @param pszPort String containing the port number  
 * @returns Non-zero socket file descriptor if successful, zero otherwise 
 * */ 
int createSocket_TCP_Listen (char * pszServer, char * pszPort);

/** Create a TCP socket that is listening on the specified port. 
 * @param pszServer String specifying the hostname / IP address (may be NULL)
 * @param pszPort String containing the port number  
 * @param nBacklog Number of connections that can be waiting in a backlog
 * @returns Non-zero socket file descriptor if successful, zero otherwise 
 * */ 
int createSocket_TCP_Listen (char * pszServer, char * pszPort, int nBacklog);


#endif


