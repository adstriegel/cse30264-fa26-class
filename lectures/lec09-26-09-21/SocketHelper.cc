
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>

#include "SocketHelper.h"

/* Create a TCP socket that has completed the listen step for initialization
 * on a particular port that listens effectively for any TCP connection to this
 * specific machine for that port
 */
int createSocket_TCP_Listen (uint16_t nPort)
{
    char szPortInfo[10];

    sprintf(szPortInfo, "%d", nPort);

    return createSocket_TCP_Listen (NULL, szPortInfo, DEFAULT_LISTEN_BACKLOG);
}

/* Create a TCP socket that has completed the listen step for initialization
 * on a particular port that listens for connections to the specified server
 * information if given (non-NULL) or any associated IP address for this host
 * if unspecified (pszServer == NULL)
 *
 * The port number is provided as a C-style string (null-terminated).
 *
 * A default setting is used for the allowed number of backlog connections that
 * are waiting to be processed by the accept command.
 */
int createSocket_TCP_Listen (char * pszServer, char * pszPort)
{
    return createSocket_TCP_Listen (pszServer, pszPort, DEFAULT_LISTEN_BACKLOG);
}

int createSocket_TCP_Listen (char * pszServer, char * pszPort, int nBacklog)
{
    // This code is adapted from Beej's Network Programming guide which has a fantastic
    //  primer on writing network code.  This is the server variant of the code which
    //  is drawn from here:
    //
    //  https://beej.us/guide/bgnet/examples/server.c
    //

    int     serverSocket;       // This is what we will create and return
    struct addrinfo hints, *servinfo, *p;
    struct sockaddr_storage their_addr; // connector's address information
    socklen_t sin_size;
    struct sigaction sa;
    int yes=1;
    char s[INET6_ADDRSTRLEN];

    int rv;


    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE; // use my IP

    // Retrieve the address information pointer to browse what choices might be
    //  available
    if ((rv = getaddrinfo(pszServer, pszPort, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 0;
    }

    // loop through all the results and bind to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((serverSocket = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("server: socket");
            continue;
        }

        if (setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &yes,
                sizeof(int)) == -1) {
            // Since we did get it created, we should close up shop
            close(serverSocket);
            perror("setsockopt");
            continue;
        }

        if (::bind(serverSocket, p->ai_addr, p->ai_addrlen) == -1) {
            // Since we did get it created, we should close up shop
            close(serverSocket);
            perror("server: bind");
            continue;
        }

        break;
    }

    freeaddrinfo(servinfo); // all done with this structure

    if (p == NULL)  {
        fprintf(stderr, "server: failed to bind\n");
        return 0;
    }

    if (listen(serverSocket, nBacklog) == -1) {
        perror("listen");
        // Since we did get it created, we should close up shop
        close(serverSocket);
        return 0;
    }

    return serverSocket;
}
