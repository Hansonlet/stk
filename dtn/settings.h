#pragma once

#include<iostream>
#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<string>
#include<vector>
#include<map>
#include<set>
#include<algorithm>
#include<list>
#include<queue>
#include<ctime>
#include<fstream>
#include<sstream>
#include<unordered_map>
#include<unordered_set>
#include<random>
#include<stack>

#include "Packet.h"
#include "Node.h"

using namespace std;

extern ofstream packet_out;
//extern ofstream buffer_out;
extern ofstream hops_out;
extern ofstream temp_result;
extern ofstream result;

const float SIMULATOR_TIME = 2448000;
const int SIMULATOR_TIME_INT = 2448000;
extern float NOW_TIME;
/////////////////////////////////////////////////////////////
const int CONNECTED_ABILITY = 6;//Ka:4 Laser:6
const int USERS_PER_MOON = 2;
const int USERS_PER_SHIP = 1;
const float MOONBUFFERSIZE = 1024 * 128;//一分钟容量，约1.13G。Default:10G
const float SATELLITEBUFFERSIZE = 512;//Default:500M
const float REALTIME_MAXDELAY = 3.1;//单位是秒 Default:3.1
const float UNREALTIME_MAXDELAY = 60 * 30;

const int moon_Surface_Num = 3;
const int moon_Ship_Num = 3;
const int moon_Node_Num = moon_Surface_Num + moon_Ship_Num;
const int satellite_Node_Num = 3;
const int earth_Node_Num = 1;
const int sum_Num = moon_Node_Num + satellite_Node_Num + earth_Node_Num;

const float TOTAL_BANDWIDTH = 155.0 / 8;	//Ka:155  Laser:622
const float MAX_PER_NODE_BANDWIDTH = 40.0 / 8;
const float MAX_PER_SHIP_BANDWIDTH = 15.0 / 8;
const float UP_TOTAL_BANDWIDTH = 10.0 / 8;
extern float SENDRATE[sum_Num];
extern float SPARED_RATE;

const string TRACE_STR = "D:\\3_1\\";
/////////////////////////////////////////////////////////////
extern unordered_map<string, vector<vector<float>>> isConnected_hashmap;
extern bool isConnected[SIMULATOR_TIME_INT + 1][sum_Num][sum_Num];

extern int established_counts[sum_Num];
extern int established_to_which[sum_Num];

extern queue<Packet> SENT_QUEUE[sum_Num];

extern Node NODE_OBJECT[sum_Num];

extern long long RECEIVED_PACKETS_REALTIME;
extern long long RECEIVED_PACKETS_UNREALTIME;
extern double TOTAL_DELAY_REALTIME;
extern double TOTAL_DELAY_UNREALTIME;
