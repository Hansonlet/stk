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

using namespace std;

class Packet {
public:
	enum class Packet_Type { VEDIO, AUDIO, TELEMETRY, ORDER };
	Packet_Type packet_type;

	int ori;
	int dst;
	int last_hop;
	int hop_counts;
	float lasthop_Send_Time;
	float receive_Time;
	long long seq;
	//int ith;
	float generate_time;
	float queue_delay;
	float total_queue_delay;
	float size;
	int retransmission_Times;
	float retransmission_Time_Stamp;
	vector<int> hops;

	float GetPropogation_Delay();

	Packet(Packet_Type input_packet_type, int input_ori, int input_dst, int input_last_hop, long long input_seq, float input_generate_time, float input_size, int input_retransmission_Times) :
		packet_type(input_packet_type),
		ori(input_ori),
		dst(input_dst),
		last_hop(input_last_hop),
		hop_counts(0),
		lasthop_Send_Time(input_generate_time),
		receive_Time(input_generate_time),
		seq(input_seq),
		generate_time(input_generate_time),
		queue_delay(0),
		total_queue_delay(0),
		size(input_size),
		retransmission_Times(input_retransmission_Times),
		retransmission_Time_Stamp(input_generate_time) {
		hops.reserve(4);
		for (int i = 0; i < 4; i++) {
			hops.push_back(-1);
		}
	}
	Packet(const Packet& temp) :
		ori(temp.ori),
		dst(temp.dst),
		last_hop(temp.last_hop),
		hop_counts(temp.hop_counts),
		lasthop_Send_Time(temp.lasthop_Send_Time),
		receive_Time(temp.receive_Time),
		seq(temp.seq),
		generate_time(temp.generate_time),
		queue_delay(temp.queue_delay),
		total_queue_delay(temp.total_queue_delay),
		size(temp.size),
		retransmission_Times(temp.retransmission_Times),
		retransmission_Time_Stamp(temp.retransmission_Time_Stamp),
		hops(temp.hops),
		packet_type(temp.packet_type) {}
};
