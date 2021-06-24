#include "Moon.h"
#include "settings.h"
           
//void
//Moon::GeneratePacket() {
//	int times;
//	if (_node_ID < moon_Surface_Num) { times = USERS_PER_MOON; }
//	else { times = USERS_PER_SHIP; }
//	static long long seq = 0;
//	for (int i = 0; i < times; ++i) {
//		Packet vedio_packet(_node_ID, sum_Num - 1, _node_ID, ++seq, NOW_TIME, 1, 0);
//		vedio_packet.hops[0] = _node_ID;
//		vedio_packet.packet_type = Packet::VEDIO;
//		_m_queue.push(vedio_packet);
//		_buffer_size_used += 1;
//		Packet audio_packet(_node_ID, sum_Num - 1, _node_ID, ++seq, NOW_TIME, 0.004, 0);
//		audio_packet.hops[0] = _node_ID;
//		audio_packet.packet_type = Packet::AUDIO;
//		_m_queue.push(audio_packet);
//		_buffer_size_used += 0.004;
//		Packet telemetry_packet(_node_ID, sum_Num - 1, _node_ID, ++seq, NOW_TIME, 0.125, 0);
//		telemetry_packet.hops[0] = _node_ID;
//		telemetry_packet.packet_type = Packet::TELEMETRY;
//		_m_queue.push(telemetry_packet);
//		_red_queue.push_back(telemetry_packet);
//		_buffer_size_used += 0.125;
//	}
//}
//
//void
//Moon::SendPacket() {
//	int nexthop = ChooseNextHop();
//	if (nexthop == -1) { return; }
//	Reset();
//	float total_bandwidth = _available_bandwidth;
//
//	while (!_m_queue.empty()) {
//		Packet temp = _m_queue.front();
//		temp.last_hop = _node_ID;
//		if (_available_bandwidth >= temp.size) {//正常发包
//			//cout << _node_ID << " send " << temp.seq << " to " << nexthop << endl;
//			temp.queue_delay = (total_bandwidth - _available_bandwidth) / total_bandwidth;
//			temp.lasthop_Send_Time = max(NOW_TIME, temp.receive_Time) + temp.queue_delay;
//			temp.total_queue_delay += temp.queue_delay;
//			SENT_QUEUE[nexthop].push(temp);
//			_available_bandwidth -= temp.size;
//			_m_queue.pop();
//			if (_node_ID >= moon_Node_Num || temp.packet_type != Packet::TELEMETRY) {
//				_buffer_size_used -= temp.size;
//			}
//		}
//		else {//带宽用完了，剩下的包排队延迟都加1秒
//			int T = _m_queue.size();
//			while (T--) {
//				Packet temp = _m_queue.front();
//				++temp.total_queue_delay;
//				_m_queue.pop();
//				_m_queue.push(temp);
//			}
//			break;
//		}
//	}
//}
//
//int
//Moon::ChooseNextHop() {
//	////L点卫星，直接传回去就可以了
//	//if (_node_ID >= moon_Node_Num && _node_ID < moon_Node_Num + L_Node_Num) {
//	//	if (isConnected[(int)NOW_TIME][_node_ID][sum_Num - 1]) {
//	//		Modify_Connected_State(sum_Num - 1);
//	//		return sum_Num - 1;
//	//	}
//	//	else {
//	//		return -1;
//	//	}
//	//}
//
//	//绕月卫星寻找下一跳
//	if (_node_ID >= moon_Node_Num) {
//		pair<int, float> temp_nexthop = Sa_FindNextHop(_node_ID);
//		if (temp_nexthop.first == -1) { return -1; }
//		if (isConnected[(int)NOW_TIME][_node_ID][temp_nexthop.first]) {
//			Modify_Connected_State(temp_nexthop.first);
//			return temp_nexthop.first;
//		}
//		else {
//			return -1;
//		}
//	}
//
//	//可以与地球直连的月球节点寻找下一跳	
//	if (_node_ID == 0 || _node_ID == 3) {
//		if (isConnected[(int)NOW_TIME][_node_ID][sum_Num - 1]) {
//			Modify_Connected_State(sum_Num - 1);
//			return sum_Num - 1;
//		}
//	}
//
//	//月球节点不能直连完成递交时，选择一个卫星作为下一跳
//	/*int temp_counts;
//	if (_node_ID < moon_Surface_Num) { temp_counts = USERS_PER_MOON; }
//	else if (_node_ID < moon_Node_Num) { temp_counts = USERS_PER_SHIP; }
//	else { temp_counts = 1; }*/
//	vector<pair<int, float>> nexthop;
//	pair<int, float> temp_nexthop;
//	float temp_queue_delay;
//	for (int i = moon_Node_Num; i < sum_Num - 1; ++i) {
//		if (isConnected[(int)NOW_TIME][_node_ID][i] && Can_Connect(_node_ID, i)) {
//			////L点
//			//if (i < moon_Node_Num + L_Node_Num) {
//			//	temp_nexthop.first = i;
//			//	temp_nexthop.second = GetCost(_node_ID, i);
//			//	nexthop.push_back(temp_nexthop);
//			//}
//			//else {
//				//其他卫星
//			temp_nexthop = Sa_FindNextHop(i);
//			temp_nexthop.first = i;
//			nexthop.push_back(temp_nexthop);
//			//}
//		}
//	}
//	//飞船也可以选择月球（赤道）基站作为中继
//	if (_node_ID >= moon_Surface_Num && _node_ID < moon_Node_Num) {
//		if (isConnected[(int)NOW_TIME][_node_ID][3]) {
//			float temp_time_to3 = GetCost(_node_ID, 3);
//			temp_nexthop.first = 3;
//			temp_queue_delay = NODE_OBJECT[3]->Get_BufferSizeUsed() / (SENDRATE[3] - SPARED_RATE);
//			temp_nexthop.second = temp_time_to3 + temp_queue_delay +
//				GetCost(3, sum_Num - 1, temp_time_to3 + temp_queue_delay);
//			nexthop.push_back(temp_nexthop);
//		}
//	}
//	//0和3可以等待直连机会
//	if (_node_ID == 0 || _node_ID == 3) {
//		temp_nexthop.first = -1;
//		temp_nexthop.second = GetCost(_node_ID, sum_Num - 1);
//		nexthop.push_back(temp_nexthop);
//	}
//	if (nexthop.size() == 0) { return -1; }
//	//选择代价最小的中继
//	sort(nexthop.begin(), nexthop.end(), [](pair<int, float> a, pair<int, float> b) {
//		if (abs(a.second - b.second) < 0.01) {
//			return established_counts[a.first] < established_counts[b.first];
//		}
//		else {
//			return a.second < b.second;
//		}
//		});
//
//	if (nexthop[0].first == -1) { return -1; }
//	else if (isConnected[(int)NOW_TIME][_node_ID][nexthop[0].first]) {
//		Modify_Connected_State(nexthop[0].first);
//		return nexthop[0].first;
//	}
//	else {
//		return -1;
//	}
//}