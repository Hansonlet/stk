#include "settings.h"

ofstream packet_out("packet.txt");
//ofstream buffer_out("buffer.txt");
ofstream hops_out("hops.txt");
ofstream temp_result("temp_result.txt");
ofstream result("result.txt");

float NOW_TIME = 1;

float SENDRATE[sum_Num];
float SPARED_RATE = 1.0;

unordered_map<string, vector<vector<float>>> isConnected_hashmap;
bool isConnected[SIMULATOR_TIME_INT + 1][sum_Num][sum_Num];

int established_counts[sum_Num];
int established_to_which[sum_Num];

queue<Packet> SENT_QUEUE[sum_Num];
Node NODE_OBJECT[sum_Num];

long long RECEIVED_PACKETS_REALTIME = 0;
long long RECEIVED_PACKETS_UNREALTIME = 0;
double TOTAL_DELAY_REALTIME = 0;
double TOTAL_DELAY_UNREALTIME = 0;