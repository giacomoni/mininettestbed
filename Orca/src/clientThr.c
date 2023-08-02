//============================================================================
// Author      : Soheil Abbasloo
// Version     : 1.0
//============================================================================

/*
  MIT License
  Copyright (c) Soheil Abbasloo 2020 (ab.soheil@gmail.com)

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>  
#include <sys/socket.h>  
#include <netinet/in.h>  
#include <arpa/inet.h> 
#include <pthread.h>
#include <errno.h>
#include <netinet/tcp.h>
#include <time.h>
#include <inttypes.h>
#include <sys/time.h>

#include "common.h"

#define DBG 0
#define HASH_RANGE 5
#define TCP_BBR_EN_MAXDEL 33
#define TCP_BBR_EN_PRBRTT 34
#define TCP_BBR_TRGTDEL_MS 35
#define TCP_BBR_MINRTTWIN_SEC 36
#define TCP_BBR_PRBERTTMDE_MS 37
#define TCP_BBR_BWAUTO 38
#define TCP_BBR_BWVAL 39
#define TCP_BBR_CWNDRVGAIN 40
#define TCP_BBR_DEBUG 41

#define BUFSIZE 200


struct timeval tv_start;	//Start time (after three way handshake)
struct timeval tv_end;		//End time

//Print usage information
void usage();
int check_input(int data_size, int deadline, int is_agnostic)
{
	return 1;                       // :D
}
uint64_t raw_timestamp( void )
{
    struct timespec ts;
    clock_gettime( CLOCK_REALTIME, &ts );
    uint64_t us = ts.tv_nsec / 1000;
    us += (uint64_t)ts.tv_sec * 1000000;
    return us;
}

uint64_t initial_timestamp( void )
{
        static uint64_t initial_value = raw_timestamp();
        return initial_value;
}

uint64_t timestamp( void )
{
        return raw_timestamp() - initial_timestamp();
}

int main(int argc, char **argv)
{
    uint64_t start_timestamp=10;
    FILE *filep;
    char line[4096];
//    usleep(500000);
	int connected=0;
    int i;
    start_timestamp=start_timestamp*1000;

	if(argc!=5)
	{
		usage();
        for(int i=0;i<argc;i++)
        {   
            DBGERROR("%s\n",argv[i]);
        }
           DBGERROR("ARGC:%d\n",argc);
                
		return 0;
	}

	char *savePtr;
	char* server=(char*)malloc(16*sizeof(char));;	//IP address (e.g. 192.168.101.101) 
	char query[100];	                                //query=data_size+' '+deadline+' '+agnostic
	int port;                                   	//TCP port number
	int data_size;	                                //Request data size (KB)	We allocate 20bits for this in nfmark [0, 4GB]
	int flowid;	
	char *dst_ip;

	int sockfd;	                                    //Socket
	struct sockaddr_in servaddr;                	//Server address (IP:Port)
	struct sockaddr_in clientaddr;              	//client address (IP:Port)

	int len;                                    	//Read length
	char buf[BUFSIZ];                           	//Receive buffer
	unsigned long fct;	                            //Flow Completion Time

	//Initialize ‘server’
	memset(server,'\0',16);
	//Initialize 'query'
	memset(query,'\0',150);

	//Get server address
	server=argv[1];
	//Get deadline information: char* to int
	flowid=atoi(argv[2]);
	//Get data_size: char* to int
    //data_size=atoi(argv[3]);
    //Following line won't impact the code in this version: Server always sends data (no size request will be handled in this project ;) )
    data_size=2700;
	//Get is_agnostic: char* to int
    //Following line won't impact the code in this version: Server always sends data (We don't need interface bounding in this project ;) )
    //dst_ip=argv[4];
//   dst_ip="10.10.10.10";
    //Get TCP port: char* to int
	port=atoi(argv[3]);
	float interval = atof(argv[4]);
    char time_s [50];
    char time_us[37];
    int cx;
    uint64_t t=start_timestamp;
//    printf("%"PRIu64, t);
    cx = snprintf ( time_s, 49, "%" PRIu64, t);
    DBGPRINT(DBG,2,"time_s:%" PRIu64"\n",t);
    
	//If the inputs are legal
	if(check_input(data_size,0,0)==0)
	{
		DBGPRINT(0,0,"Illegal input!\n");
		return 0;
	}
	else
	{
		strcat(query,argv[1]);
		strcat(query," ");
		strcat(query,argv[2]);
		strcat(query," ");
//		strcat(query,argv[3]);
        strcat(query,"2700");
		strcat(query," ");
		strcat(query,"10.10.10.10");
//      strcat(query,argv[4]);
		strcat(query," ");
        strcat(query,time_s);
        strcat(query," ");
//		strcat(query,argv[3]);
        strcat(query,"2700");
	}
		
	//Init sockaddr_in
	memset(&servaddr,0,sizeof(servaddr));
	servaddr.sin_family=AF_INET;
	//IP address
	servaddr.sin_addr.s_addr=inet_addr(server);
	//Port number
	servaddr.sin_port=htons(port);

	//Init sockaddr_in
//	memset(&clientaddr,0,sizeof(clientaddr));
//	clientaddr.sin_family=AF_INET;
	//IP address
//	clientaddr.sin_addr.s_addr=inet_addr(dst_ip);
	//Port number

	//Init socket
	if((sockfd=socket(PF_INET,SOCK_STREAM,0))<0)
	{
		DBGMARK(0,0,"socket error:%s\n",strerror(errno));
		return 0;
	}
	int reuse = 1;
//	gettimeofday(&tv_start,NULL);
	if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &reuse, sizeof(reuse)) < 0)
	{
		DBGMARK(0,0,"ERROR: set TCP_NODELAY option %s\n",strerror(errno));
		close(sockfd);
		return 0;
	}
	DBGPRINT(DBG,5,"%s ---\n",inet_ntoa(servaddr.sin_addr));

	//bind it to correct interface
    //We don't need this for this project! :D
/*	if(bind(sockfd,(struct sockaddr *)&clientaddr,sizeof(struct sockaddr))<0)
	{
		DBGMARK(0,0,"bind error add:%s : %s",dst_ip,strerror(errno));
		return 0;
	}
*/
	//Establish connection
    for(i=0;i<120;i++)
    {
        if(connect(sockfd,(struct sockaddr *)&servaddr,sizeof(struct sockaddr))<0)
        {
            DBGPRINT(0,0,"Trying to connect to %s\n",server);
            usleep(500000);
        }
        else
        {
            connected=1;
            DBGPRINT(0,0,"Connected!\n");
            break;
        }
    }
    if(!connected)
    {
        DBGPRINT(0,0,"No success after 120 tries :(\n");
        close(sockfd);
        return 0;
    }

    DBGPRINT(DBG,5,"%s ---\n",inet_ntoa(servaddr.sin_addr));
    
	//Send request
	len=strlen(query);
	while(len>0)
	{
		len-=send(sockfd,query,strlen(query),0);
	}
    //DBGPRINT(0,0,"Request is sent to server ...\n");
    DBGMARK(DBG,1,"after sending request\n");
	//Receive data
	struct timeval t1, t2, tStart, tEnd, timeresult;
    	double elapsedTime, totalElapsedTime;

        //start timer
	gettimeofday(&t1, NULL);
	gettimeofday(&tStart, NULL);
	double lensum = 0;
	double totalLenSum = 0;
	double tick = 0;
	FILE *fptr;
	char* filename;
	char scheme[BUFSIZE];
   	char *envvarscheme = "SCHEME";

	char bw[BUFSIZE];
   	char *envvarbw = "BW";

	char delay[BUFSIZE];
   	char *envvardelay = "DELAY";

	char qsize[BUFSIZE];
   	char *envvarqsize = "QSIZE";

	char resultsroot[BUFSIZE];
   	char *envvarresultsroot = "RESULTS_ROOT";

		 // Make sure envar actually exists
	    if(!getenv(envvarscheme)){
		fprintf(stderr, "The environment variable %s was not found.\n", envvarscheme);
		exit(1);
	    }

	    // Make sure the buffer is large enough to hold the environment variable
	    // value. 
	    if(snprintf(scheme, BUFSIZE, "%s", getenv(envvarscheme)) >= BUFSIZE){
		fprintf(stderr, "BUFSIZE of %d was too small. Aborting\n", BUFSIZE);
		exit(1);
	    }

	 // Make sure envar actually exists
	    if(!getenv(envvarbw)){
		fprintf(stderr, "The environment variable %s was not found.\n", envvarbw);
		exit(1);
	    }

	    // Make sure the buffer is large enough to hold the environment variable
	    // value. 
	    if(snprintf(bw, BUFSIZE, "%s", getenv(envvarbw)) >= BUFSIZE){
		fprintf(stderr, "BUFSIZE of %d was too small. Aborting\n", BUFSIZE);
		exit(1);
	    }
	 // Make sure envar actually exists
	    if(!getenv(envvardelay)){
		fprintf(stderr, "The environment variable %s was not found.\n", envvardelay);
		exit(1);
	    }

	    // Make sure the buffer is large enough to hold the environment variable
	    // value. 
	    if(snprintf(delay, BUFSIZE, "%s", getenv(envvardelay)) >= BUFSIZE){
		fprintf(stderr, "BUFSIZE of %d was too small. Aborting\n", BUFSIZE);
		exit(1);
	    }
	// Make sure envar actually exists
	    if(!getenv(envvarqsize)){
		fprintf(stderr, "The environment variable %s was not found.\n", envvarqsize);
		exit(1);
	    }

	    // Make sure the buffer is large enough to hold the environment variable
	    // value. 
	    if(snprintf(qsize, BUFSIZE, "%s", getenv(envvarqsize)) >= BUFSIZE){
		fprintf(stderr, "BUFSIZE of %d was too small. Aborting\n", BUFSIZE);
		exit(1);
	    }

	    // Make sure envar actually exists
	    if(!getenv(envvarresultsroot)){
		fprintf(stderr, "The environment variable %s was not found.\n", envvarresultsroot);
		exit(1);
	    }

	    // Make sure the buffer is large enough to hold the environment variable
	    // value. 
	    if(snprintf(resultsroot, BUFSIZE, "%s", getenv(envvarresultsroot)) >= BUFSIZE){
		fprintf(stderr, "BUFSIZE of %d was too small. Aborting\n", BUFSIZE);
		exit(1);
	    }
	

	asprintf(&filename, "%s/goodputs/goodput_%s_%smbps_%sdel_%s_q_flow_%d.txt", resultsroot,scheme, bw, delay, qsize, flowid);

	fptr = fopen(filename,"w");
	if(fptr == NULL)
	   {
	      printf("Error!");   
	      exit(1);             
	   }
	fprintf(fptr,"time,goodput,bytes,totalgoodput\n");
	fflush(fptr);
	fsync(fileno(fptr));

	while(1)
	{	

		len=recv(sockfd,buf,BUFSIZ,0);
		if(len<=0)
		{
			//DBGPRINT(DBG,2,"len:%d\n",len);	
			break;
		}else{
		gettimeofday(&t2, NULL);

		timersub(&t2, &t1, &timeresult);
		elapsedTime = timeresult.tv_sec + (double)(timeresult.tv_usec)/1000000; 
		lensum = lensum + (double)len;

		timersub(&t2, &tStart, &timeresult);
		totalElapsedTime = timeresult.tv_sec + (double)(timeresult.tv_usec)/1000000; 
		totalLenSum =  totalLenSum + (double)len;
		if(elapsedTime >= interval){
			tick = tick+elapsedTime;
       			fprintf(fptr,"%f,%f,%f,%f\n", tick ,(((double)lensum)/elapsedTime * 8)/(1000*1000),totalLenSum, (((double)totalLenSum)/totalElapsedTime * 8)/(1000*1000));
			fflush(fptr);
			fsync(fileno(fptr));
			lensum = 0;
			t1 = t2;

		}
		}
		
	}
	
	gettimeofday(&tEnd, NULL);
	totalElapsedTime = (tEnd.tv_sec - tStart.tv_sec); 
       	fprintf(fptr,"%f,%f\n", totalElapsedTime,(((double)totalLenSum)/totalElapsedTime * 8)/(1000*1000));
	fflush(fptr);
	fsync(fileno(fptr));

    //Close connection
    close(sockfd);
    fclose(fptr);
    free(filename);
    DBGMARK(DBG,1,"after receiving data\n\n");
    return 0;
}

void usage()
{
	DBGWARN("./client [server IP address] [flowid] [server port] [interval]\n");
}


