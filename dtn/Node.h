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

#include"Packet.h"

using namespace std;

class Node {
public:
	Node() :_buffer_size_used(0) {
		_red_queue.reserve(8192);
	}
	void SetBuffersize(float input_buffersize) {
		_buffer_size = input_buffersize;
	};
	void GeneratePacket();
	void SendPacket();
	void ReceivePacket();
	void Retransmit(Packet temp);
	void setID(int i) { _node_ID = i; }
	int getID() { return _node_ID; }
	void setBufferSize(float size) { _buffer_size = size; }
	float Get_BufferSizeUsed();
	float Get_BufferSize() { return _buffer_size; }
	void CheckBuffer();
	void Erase_Red_Queue(long long seq);
	void Delete_Connect(int i);

protected:
	int ChooseNextHop();
	void Reset();
	float GetCost(int caculate_Node_ID, int dst, int future_time = 0);
	void Modify_Connected_State(int i);
	pair<int, float> Sa_FindNextHop(int id);
	bool Can_Connect(int sender_ID, int i);
	void Out_Message(Packet& temp, float delay);

	queue<Packet> _m_queue;
	//queue<Packet> _m_queue0;
	//queue<Packet> _m_queue1;
	//queue<Packet> _m_queue2;
	//queue<Packet> _m_queue3;

	set<long long> _record_set;
	vector<Packet> _red_queue;
	int _node_nums;//该处有几个节点
	float _max_bandwidth;
	float _available_bandwidth;
	//float _up_bandwidth;
	int _node_ID;
	float _buffer_size;
	float _buffer_size_used;
};
