#include "settings.h"

void
Node::GeneratePacket() {
	int times;
	if (_node_ID < moon_Surface_Num) { times = USERS_PER_MOON; }
	else { times = USERS_PER_SHIP; }
	static long long seq = 0;
	for (int i = 0; i < times; ++i) {
		Packet vedio_packet(Packet::Packet_Type::VEDIO, _node_ID, sum_Num - 1, _node_ID, ++seq, NOW_TIME, 1.25, 0);
		vedio_packet.hops[0] = _node_ID;
		_m_queue.push(vedio_packet);
		_buffer_size_used += 1.25;

		Packet audio_packet(Packet::Packet_Type::AUDIO, _node_ID, sum_Num - 1, _node_ID, ++seq, NOW_TIME, 0.002, 0);
		audio_packet.hops[0] = _node_ID;
		_m_queue.push(audio_packet);
		_buffer_size_used += 0.002;

		Packet telemetry_packet(Packet::Packet_Type::TELEMETRY, _node_ID, sum_Num - 1, _node_ID, ++seq, NOW_TIME, 0.25, 0);
		telemetry_packet.hops[0] = _node_ID;
		_m_queue.push(telemetry_packet);
		_red_queue.push_back(telemetry_packet);
		_buffer_size_used += 0.25;
	}
}

void
Node::SendPacket() {
	int nexthop = ChooseNextHop();
	if (nexthop == -1) { return; }
	Reset();
	float total_bandwidth = _available_bandwidth;

	while (!_m_queue.empty()) {
		Packet temp = _m_queue.front();
		temp.last_hop = _node_ID;
		if (_available_bandwidth >= temp.size) {//正常发包
			//cout << _node_ID << " send " << temp.seq << " to " << nexthop << endl;
			temp.queue_delay = (total_bandwidth - _available_bandwidth) / total_bandwidth;
			temp.lasthop_Send_Time = max(NOW_TIME, temp.receive_Time) + temp.queue_delay;
			temp.total_queue_delay += temp.queue_delay;
			SENT_QUEUE[nexthop].push(temp);
			_available_bandwidth -= temp.size;
			_m_queue.pop();
			if (!(temp.packet_type == Packet::Packet_Type::TELEMETRY && temp.ori == _node_ID)) {
				_buffer_size_used -= temp.size;
			}
		}
		else {//带宽用完了，剩下的包排队延迟都加1秒
			int T = _m_queue.size();
			while (T--) {
				Packet temp = _m_queue.front();
				++temp.total_queue_delay;
				_m_queue.pop();
				_m_queue.push(temp);
			}
			break;
		}
	}
}

void
Node::ReceivePacket() {
	static unordered_map<long long, bool> received_packets;
	float delay;
	if (_node_ID == sum_Num - 1) { delay = 1.28; }
	else { delay = 0.02; }
	int T = SENT_QUEUE[_node_ID].size();
	while (T--) {
		Packet& temp = SENT_QUEUE[_node_ID].front();
		//处理在NOW_TIME~NOW_TIME+1之间到达的数据包
		if (/*temp.lasthop_Send_Time + delay >= NOW_TIME &&*/ temp.lasthop_Send_Time + delay < NOW_TIME + 1) {//可以收
			if (!isConnected[(int)NOW_TIME][temp.last_hop][_node_ID]) {//链接不在了
				//释放链接
				SENT_QUEUE[_node_ID].pop();
				continue;
			}
			++temp.hop_counts;
			temp.hops[temp.hop_counts] = _node_ID;
			if (_node_ID == temp.dst) {//到了
				if (temp.seq > 1166400 && temp.seq <= 64929600) {//只要12h-27天20h内的  //每秒27个包
					if (received_packets[temp.seq] == false) {
						Out_Message(temp, delay);
						received_packets[temp.seq] = true;
					}
				}
				else {
					if (temp.packet_type == Packet::Packet_Type::TELEMETRY) {
						NODE_OBJECT[temp.ori].Erase_Red_Queue(temp.seq);
						if (_record_set.find(temp.seq) == _record_set.end()) {//没收过
							_record_set.insert(temp.seq);
						}
					}
				}
			}
			else {//中继，存着
				temp.receive_Time = temp.lasthop_Send_Time + delay;
				temp.queue_delay = 0;
				_m_queue.push(temp);
				_buffer_size_used += temp.size;
			}
		}
		else { //还在路上
			SENT_QUEUE[_node_ID].push(temp);
		}
		SENT_QUEUE[_node_ID].pop();
	}
}

void
Node::Retransmit(Packet temp) {
	_red_queue.erase(_red_queue.begin());
	if (temp.retransmission_Times < 1){//&& UNREALTIME_MAXDELAY < 10 * 60) {
		++temp.retransmission_Times;
		temp.retransmission_Time_Stamp = NOW_TIME;
		_red_queue.push_back(temp);
		_m_queue.push(temp);
	}
	else {//超过1次就不传了
		_buffer_size_used -= temp.size;
	}
}

float
Node::Get_BufferSizeUsed() {
	return _buffer_size_used;
}

void
Node::CheckBuffer() {
	//重传
	while (!_red_queue.empty()) {
		//超时UNREALTIME_MAXDELAY重传
		if (_red_queue[0].retransmission_Time_Stamp + UNREALTIME_MAXDELAY < NOW_TIME){ 
			Retransmit(_red_queue[0]);
		}
		else { break; }
	}

	//清理超时包（实时4s/非实时1min-20min）
	int T = _m_queue.size();
	while (T--) {
		Packet temp = _m_queue.front();
		_m_queue.pop();
		//非实时的超时
		if ((temp.packet_type == Packet::Packet_Type::VEDIO || temp.packet_type == Packet::Packet_Type::TELEMETRY || temp.packet_type == Packet::Packet_Type::AUDIO) && NOW_TIME - temp.generate_time > UNREALTIME_MAXDELAY) {
			if (!(temp.packet_type == Packet::Packet_Type::TELEMETRY && temp.ori == _node_ID)) {
				_buffer_size_used -= temp.size;
			}
			continue;
		}
		//没超时
		else {
			_m_queue.push(temp);
		}
	}

	//清理超出存储能力包
	while (_buffer_size_used > _buffer_size && !_m_queue.empty()) {
		if (!(_m_queue.front().packet_type == Packet::Packet_Type::TELEMETRY && _m_queue.front().ori == _node_ID)) {
			_buffer_size_used -= _m_queue.front().size;
		}
		_m_queue.pop();
	}
	while (_buffer_size_used > _buffer_size && !_red_queue.empty()) {//发送队列清完了缓存还是不够
		_buffer_size_used -= _red_queue.front().size;
		_red_queue.erase(_red_queue.begin());
	}
}

void
Node::Erase_Red_Queue(long long seq) {
	for (vector<Packet>::iterator it = _red_queue.begin(); it != _red_queue.end(); it++) {
		if ((*it).seq == seq) {
			_buffer_size_used -= (*it).size;
			_red_queue.erase(it);
			break;
		}
	}
}

void
Node::Delete_Connect(int i) {
	established_to_which[_node_ID] = -1;
	//都不是月球用户，就不算连接数量了
	if (_node_ID >= moon_Node_Num && i >= moon_Node_Num) { return; }
	int sender_temp_counts;
	if (_node_ID < moon_Surface_Num) { sender_temp_counts = USERS_PER_MOON; }
	else if (_node_ID < moon_Node_Num) { sender_temp_counts = USERS_PER_SHIP; }
	else { sender_temp_counts = 1; }
	int receiver_temp_counts;
	if (i < moon_Surface_Num) { receiver_temp_counts = USERS_PER_MOON; }
	else if (i < moon_Node_Num) { receiver_temp_counts = USERS_PER_SHIP; }
	else { receiver_temp_counts = 1; }
	//月表节点
	if (_node_ID < moon_Surface_Num) {
		if (established_to_which[i] == _node_ID) {
			established_counts[i] -= sender_temp_counts - receiver_temp_counts;
		}
		else {
			established_counts[_node_ID] -= receiver_temp_counts;
			established_counts[i] -= sender_temp_counts;
		}
	}
	//我是普通节点，你是月表节点
	else if (i < moon_Surface_Num) {
		if (established_to_which[i] == _node_ID) {
			established_counts[_node_ID] -= receiver_temp_counts - sender_temp_counts;
		}
		else {
			established_counts[_node_ID] -= sender_temp_counts;
			established_counts[i] -= sender_temp_counts;
		}
	}
	//我们都是普通节点
	else {
		if (established_to_which[i] == _node_ID) {
			return;
		}
		else {
			established_counts[_node_ID] -= receiver_temp_counts;
			established_counts[i] -= sender_temp_counts;
		}
	}
}

int
Node::ChooseNextHop() {
	//绕月卫星寻找下一跳
	if (_node_ID >= moon_Node_Num) {
		pair<int, float> temp_nexthop = Sa_FindNextHop(_node_ID);
		if (temp_nexthop.first == -1) { return -1; }
		if (isConnected[(int)NOW_TIME][_node_ID][temp_nexthop.first]) {
			Modify_Connected_State(temp_nexthop.first);
			return temp_nexthop.first;
		}
		else {
			return -1;
		}
	}

	//可以与地球直连的月球节点寻找下一跳	
	if (_node_ID == 0 || _node_ID == 1) {
		if (isConnected[(int)NOW_TIME][_node_ID][sum_Num - 1]) {
			Modify_Connected_State(sum_Num - 1);
			return sum_Num - 1;
		}
	}

	//月球节点不能直连完成递交时，选择一个卫星作为下一跳
	int temp_counts;
	if (_node_ID < moon_Surface_Num) { temp_counts = USERS_PER_MOON; }
	else if (_node_ID < moon_Node_Num) { temp_counts = USERS_PER_SHIP; }
	else { temp_counts = 1; }
	vector<pair<int, float>> nexthop;
	pair<int, float> temp_nexthop;
	float temp_queue_delay;
	for (int i = moon_Node_Num; i < sum_Num - 1; ++i) {
		if (isConnected[(int)NOW_TIME][_node_ID][i] && Can_Connect(_node_ID, i) &&
			NODE_OBJECT[i].Get_BufferSize() - NODE_OBJECT[i].Get_BufferSizeUsed() >= 2) {
			temp_nexthop = Sa_FindNextHop(i);
			temp_nexthop.first = i;
			nexthop.push_back(temp_nexthop);
		}
	}
	//飞船也可以选择月球（赤道）基站作为中继
	if (_node_ID >= moon_Surface_Num && _node_ID < moon_Node_Num) {
		if (isConnected[(int)NOW_TIME][_node_ID][0] &&
			NODE_OBJECT[0].Get_BufferSize() - NODE_OBJECT[0].Get_BufferSizeUsed() >= 2) {
			float temp_time_to0 = GetCost(_node_ID, 0);
			temp_nexthop.first = 0;
			temp_queue_delay = NODE_OBJECT[0].Get_BufferSizeUsed() / (SENDRATE[0] - SPARED_RATE);
			temp_nexthop.second = temp_time_to0 + temp_queue_delay +
				GetCost(0, sum_Num - 1, temp_time_to0 + temp_queue_delay);
			nexthop.push_back(temp_nexthop);
		}
	}
	//0和1可以等待直连机会
	if (_node_ID == 0 || _node_ID == 1) {
		temp_nexthop.first = -1;
		temp_nexthop.second = GetCost(_node_ID, sum_Num - 1);
		nexthop.push_back(temp_nexthop);
	}
	if (nexthop.size() == 0) { return -1; }
	//选择代价最小的中继
	sort(nexthop.begin(), nexthop.end(), [](pair<int, float> a, pair<int, float> b) {
		if (abs(a.second - b.second) < 0.01) {
			return established_counts[a.first] < established_counts[b.first];
		}
		else {
			return a.second < b.second;
		}
		});

	if (nexthop[0].first == -1) { return -1; }
	else if (isConnected[(int)NOW_TIME][_node_ID][nexthop[0].first]) {
		Modify_Connected_State(nexthop[0].first);
		return nexthop[0].first;
	}
	else {
		return -1;
	}
}

void
Node::Reset() {
	_available_bandwidth = SENDRATE[_node_ID];
}

float
Node::GetCost(int caculate_Node_ID, int dst, int future_time) {
	char key[10] = "";
	int i = (caculate_Node_ID < dst) ? caculate_Node_ID : dst;
	int j = (caculate_Node_ID < dst) ? dst : caculate_Node_ID;
	sprintf(key, "%dto%d", i, j);
	string key_str = key;
	if (isConnected_hashmap[key_str].size() == 0) { return INT_MAX; }
	//当前时间已经超过第一条记录时间
	if (NOW_TIME > isConnected_hashmap[key_str][0][1]) {
		isConnected_hashmap[key_str].erase(isConnected_hashmap[key_str].begin());
	}
	for (int i = 0; i < isConnected_hashmap[key_str].size(); ++i) {
		//还没到连接时间
		if (NOW_TIME + future_time < isConnected_hashmap[key_str][i][0]) {
			return isConnected_hashmap[key_str][i][0] - NOW_TIME - future_time;
		}
		//刚好在连接时间内
		else if (NOW_TIME + future_time <= isConnected_hashmap[key_str][i][1]) {
			return 0;
		}
	}
	//超过了所有可见时间，表示剩余仿真范围时间内不会见到该节点，所以cost是INT_MAX
	return INT_MAX;
}


void
Node::Modify_Connected_State(int i) {
	//如果不包含月球用户节点，不需要调整连接数
	if (_node_ID >= moon_Node_Num && i >= moon_Node_Num) {
		established_to_which[_node_ID] = i;
		return;
	}

	int sender_temp_counts;
	if (_node_ID < moon_Surface_Num) { sender_temp_counts = USERS_PER_MOON; }
	else if (_node_ID < moon_Node_Num) { sender_temp_counts = USERS_PER_SHIP; }
	else { sender_temp_counts = 1; }
	int receiver_temp_counts;
	if (i < moon_Surface_Num) { receiver_temp_counts = USERS_PER_MOON; }
	else if (i < moon_Node_Num) { receiver_temp_counts = USERS_PER_SHIP; }
	else { receiver_temp_counts = 1; }
	if (established_to_which[_node_ID] != -1 && established_to_which[_node_ID] != i) {
		Delete_Connect(established_to_which[_node_ID]);
	}
	if (established_to_which[_node_ID] != i) {
		established_to_which[_node_ID] = i;
		//receiver也在给sender发
		if (established_to_which[i] == _node_ID) {
			if (sender_temp_counts > receiver_temp_counts) {
				established_counts[i] += sender_temp_counts - receiver_temp_counts;
			}
		}
		else {
			if (_node_ID < moon_Node_Num) {
				established_counts[_node_ID] += receiver_temp_counts;
				established_counts[i] += sender_temp_counts;
			}
			//接收方是月表
			else {
				established_counts[_node_ID] += sender_temp_counts;
				established_counts[i] += sender_temp_counts;
			}
		}
	}
}

pair<int, float>
Node::Sa_FindNextHop(int id) {
	//优先卫星直接发送
	if (isConnected[(int)NOW_TIME][id][sum_Num - 1]) {
		return make_pair(sum_Num - 1, 0);
	}
	//卫星不能立马直接完成递交，比较卫星和基站代价
	else {
		vector<pair<int, float>> nexthop;
		pair<int, float> temp_nexthop;
		float temp_queue_delay;
		//如果0有余量
		if (isConnected[(int)NOW_TIME][id][0] && Can_Connect(id, 0) &&
			NODE_OBJECT[0].Get_BufferSize() - NODE_OBJECT[0].Get_BufferSizeUsed() >= 2) {
			temp_nexthop.first = 0;//月表节点0
			float temp_time_to0 = GetCost(id, 0);
			temp_nexthop.second = temp_time_to0 +
				NODE_OBJECT[0].Get_BufferSizeUsed() / (SENDRATE[0] - SPARED_RATE) +
				GetCost(0, sum_Num - 1, temp_time_to0 + NODE_OBJECT[0].Get_BufferSizeUsed() / (SENDRATE[0] - SPARED_RATE));
			nexthop.push_back(temp_nexthop);
		}
		//如果1有余量
		if (isConnected[(int)NOW_TIME][id][1] && Can_Connect(id, 1) &&
			NODE_OBJECT[1].Get_BufferSize() - NODE_OBJECT[1].Get_BufferSizeUsed() >= 2) {
			temp_nexthop.first = 1;//月表节点1
			float temp_time_to1 = GetCost(id, 1);
			temp_nexthop.second = temp_time_to1 +
				NODE_OBJECT[1].Get_BufferSizeUsed() / (SENDRATE[1] - SPARED_RATE) +
				GetCost(1, sum_Num - 1, temp_time_to1 + NODE_OBJECT[1].Get_BufferSizeUsed() / (SENDRATE[1] - SPARED_RATE));
			nexthop.push_back(temp_nexthop);
		}
		//自己携带
		temp_nexthop.first = -1;
		temp_nexthop.second = GetCost(id, sum_Num - 1);
		nexthop.push_back(temp_nexthop);
		//选一个吧
		temp_nexthop = nexthop[0];
		for (int i = 1; i < nexthop.size(); ++i) {
			if (temp_nexthop.second > nexthop[i].second) {
				temp_nexthop = nexthop[i];
			}
		}
		return temp_nexthop;
	}
}

bool
Node::Can_Connect(int sender_ID, int i) {
	if (established_to_which[sender_ID] == i) { return true; }
	int sender_temp_counts;
	if (sender_ID < moon_Surface_Num) { sender_temp_counts = USERS_PER_MOON; }
	else if (sender_ID < moon_Node_Num) { sender_temp_counts = USERS_PER_SHIP; }
	else { sender_temp_counts = 1; }
	//卫星发给月球通信站的
	if ((i == 0 || i == 1) && (sender_ID >= moon_Node_Num && sender_ID != sum_Num - 1)) {
		if (established_counts[sender_ID] < CONNECTED_ABILITY || established_to_which[i] == sender_ID) {
			return true;
		}
		else { return false; }
	}
	//月球用户节点发给卫星的
	if (sender_ID < moon_Node_Num && i >= moon_Node_Num && i != sum_Num - 1) {
		if (established_counts[i] <= CONNECTED_ABILITY - sender_temp_counts ||
			(established_counts[i] == CONNECTED_ABILITY - sender_temp_counts + 1 &&
				established_to_which[i] == sender_ID)) {
			return true;
		}
		else {
			return false;
		}
	}
	return true;
}

void
Node::Out_Message(Packet& temp, float delay) {
	//测试超10min数据的
	if (temp.packet_type == Packet::Packet_Type::TELEMETRY) {
		NODE_OBJECT[temp.ori].Erase_Red_Queue(temp.seq);
		if (_record_set.find(temp.seq) == _record_set.end()) {//没收过
			TOTAL_DELAY_UNREALTIME += (static_cast<double>(temp.lasthop_Send_Time) + static_cast<double>(delay) - static_cast<double>(temp.generate_time));
			++RECEIVED_PACKETS_UNREALTIME;
			if (temp.lasthop_Send_Time + delay - temp.generate_time > 600) {
				packet_out << "3 " << NOW_TIME << " " << temp.lasthop_Send_Time + delay - temp.generate_time << " ";
				//排队-路上-重传-不可见等待
				float propogation_delay = temp.GetPropogation_Delay();
				int retrans = temp.retransmission_Times;
				packet_out << temp.total_queue_delay << " " << propogation_delay << " " << retrans << " " << temp.lasthop_Send_Time + delay - temp.generate_time - temp.total_queue_delay - propogation_delay << endl;
				for (int i = 0; i < 4; ++i) {
					hops_out << temp.hops[i] << " ";
				}
				hops_out << endl;
			}
			_record_set.insert(temp.seq);
		}
	}
	else {
		if (temp.packet_type == Packet::Packet_Type::VEDIO) {
			TOTAL_DELAY_UNREALTIME += (static_cast<double>(temp.lasthop_Send_Time) + static_cast<double>(delay) - static_cast<double>(temp.generate_time));
			++RECEIVED_PACKETS_UNREALTIME;
		}
		else {
			TOTAL_DELAY_REALTIME += (static_cast<double>(temp.lasthop_Send_Time) + static_cast<double>(delay) - static_cast<double>(temp.generate_time));
			++RECEIVED_PACKETS_REALTIME;
		}
		if (temp.lasthop_Send_Time + delay - temp.generate_time > 600) {
			if (temp.packet_type == Packet::Packet_Type::VEDIO) {
				packet_out << "1 ";
			}
			else {
				packet_out << "2 ";
			}
			packet_out << NOW_TIME << " " << temp.lasthop_Send_Time + delay - temp.generate_time << " ";
			//排队-路上-重传-不可见等待
			float propogation_delay = temp.GetPropogation_Delay();
			packet_out << temp.total_queue_delay << " " << propogation_delay << " 0 " << temp.lasthop_Send_Time + delay - temp.generate_time - temp.total_queue_delay - propogation_delay << endl;
			for (int i = 0; i < 4; ++i) {
				hops_out << temp.hops[i] << " ";
			}
			hops_out << endl;
		}
	}
}