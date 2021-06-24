#include "load_file.h"
#include "settings.h"

void
Caculate_SendRate() {
	//卫星带宽初始化
	for (int i = moon_Node_Num; i < sum_Num - 1; ++i) {
		SENDRATE[i] = TOTAL_BANDWIDTH;
	}
	int ship_connects[sum_Num];
	memset(ship_connects, 0, sum_Num * sizeof(int));
	//分配飞船发送带宽，并减去相应卫星带宽余量
	for (int i = moon_Surface_Num; i < moon_Node_Num; ++i) {
		SENDRATE[i] = MAX_PER_SHIP_BANDWIDTH;
		if (established_to_which[i] >= moon_Surface_Num && established_to_which[i] < moon_Node_Num) {
			SENDRATE[established_to_which[i]] -= MAX_PER_SHIP_BANDWIDTH * USERS_PER_SHIP;
			ship_connects[established_to_which[i]]++;
		}
	}
	//分配月表节点发送带宽
	for (int i = 0; i < moon_Surface_Num; ++i) {
		if (established_to_which[i] == sum_Num - 1) {
			SENDRATE[i] = TOTAL_BANDWIDTH;
		}
		else if (established_to_which[i] < moon_Node_Num) {
			SENDRATE[i] = MAX_PER_SHIP_BANDWIDTH;
		}
		else {
			SENDRATE[i] = SENDRATE[established_to_which[i]] * USERS_PER_MOON /
				(established_counts[established_to_which[i]] - ship_connects[established_to_which[i]]);
			if (SENDRATE[i] > MAX_PER_NODE_BANDWIDTH) {
				SENDRATE[i] = MAX_PER_NODE_BANDWIDTH;
			}
		}
	}
	//分配卫星发送带宽
	for (int i = moon_Node_Num; i < sum_Num - 1; ++i) {
		if (established_to_which[i] == sum_Num - 1) {
			SENDRATE[i] = TOTAL_BANDWIDTH;
		}
		else if (established_to_which[i] < moon_Node_Num) {
			SENDRATE[i] = SENDRATE[i] /
				(established_counts[established_to_which[i]] - ship_connects[established_to_which[i]]);
		}
		else {
			SENDRATE[i] = MAX_PER_NODE_BANDWIDTH;
		}
	}
}

void
Output_TempResult(const vector<float>& result_maxbuffersize) {
	if ((int)NOW_TIME % 100000 == 0) {
		int total_packets_realtime = (NOW_TIME - 12 * 3600) * 9;
		int total_packets_unrealtime = (NOW_TIME - 12 * 3600) * 9 * 2;
		if (total_packets_realtime > 63763200 / 3) { total_packets_realtime = 63763200 / 3; }
		if (total_packets_unrealtime > 63763200 / 3 * 2) { total_packets_unrealtime = 63763200 / 3 * 2; }
		cout << "---------------- " << (int)NOW_TIME / 100000 << "0Ws passed ----------------" << endl << 
			(RECEIVED_PACKETS_REALTIME+ RECEIVED_PACKETS_UNREALTIME) << " / " << total_packets_realtime + total_packets_unrealtime << " received.( " <<
			static_cast<double>(RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) / static_cast<double>(total_packets_realtime+ total_packets_unrealtime) * 100 << "%)."
			<< endl;
		cout << "Max buffersize:" << endl;
		for (int i = 0; i < sum_Num - 1; ++i) {
			cout << i << ": " << result_maxbuffersize[i] << "\t";
			if (i % 7 == 6) {
				cout << endl;
			}
		}
		cout << endl;
		cout << "Average Delay: " << (TOTAL_DELAY_REALTIME + TOTAL_DELAY_UNREALTIME) / (RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) << endl;

		//file output
		temp_result << "---------------- " << (int)NOW_TIME / 100000 << "0Ws passed ----------------" << endl <<
			(RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) << " / " << total_packets_realtime + total_packets_unrealtime << " received.( " <<
			static_cast<double>(RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) / static_cast<double>(total_packets_realtime + total_packets_unrealtime) * 100 << "%)."
			<< endl;
		temp_result << "Max buffersize:" << endl;
		for (int i = 0; i < sum_Num - 1; ++i) {
			temp_result << i << ": " << result_maxbuffersize[i] << "\t";
			if (i % 6 == 5) {
				temp_result << endl;
			}
		}
		temp_result << endl;
		temp_result << "Average Delay: " << (TOTAL_DELAY_REALTIME + TOTAL_DELAY_UNREALTIME) / (RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) << endl;
	}
}

void Output_LastResult(const vector<float>& result_maxbuffersize) {
	int total_packets_realtime = (NOW_TIME - 12 * 3600) * 9;
	int total_packets_unrealtime = (NOW_TIME - 12 * 3600) * 9 * 2;
	if (total_packets_realtime > 63763200 / 3) { total_packets_realtime = 63763200 / 3; }
	if (total_packets_unrealtime > 63763200 / 3 * 2) { total_packets_unrealtime = 63763200 / 3 * 2; }
	cout << "---------------- The end ----------------" << endl <<
		RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME << " / " << total_packets_realtime + total_packets_unrealtime << " received.( " <<
		static_cast<double>(RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) / static_cast<double>(total_packets_realtime + total_packets_unrealtime) * 100 << "%)."
		<< endl;
	cout << "Max buffersize:" << endl;
	for (int i = 0; i < sum_Num - 1; ++i) {
		cout << i << ": " << result_maxbuffersize[i] << "\t";
		if (i % 6 == 5) {
			cout << endl;
		}
	}
	cout << endl;
	cout << "Average Delay: " << (TOTAL_DELAY_REALTIME+ TOTAL_DELAY_UNREALTIME) / (RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) << endl;

	//file output
	result << "---------------- The end ----------------" << endl <<
		RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME << " / " << total_packets_realtime + total_packets_unrealtime << " received.( " <<
		static_cast<double>(RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) / static_cast<double>(total_packets_realtime + total_packets_unrealtime) * 100 << "%)."
		<< endl;
	result << "Max buffersize:" << endl;
	for (int i = 0; i < sum_Num - 1; ++i) {
		result << i << ": " << result_maxbuffersize[i] << "\t";
		if (i % 6 == 5) {
			result << endl;
		}
	}
	result << endl;
	result << "Average Delay: " << (TOTAL_DELAY_REALTIME + TOTAL_DELAY_UNREALTIME) / (RECEIVED_PACKETS_REALTIME + RECEIVED_PACKETS_UNREALTIME) << endl;
}

int main() {
	cout << "-------------- Simulator Begin --------------" << endl;
	cout << "Sum Nodes: " << sum_Num << "        Total Simulator Time: " << SIMULATOR_TIME_INT << endl;
	cout << "Bandwidth: " << TOTAL_BANDWIDTH << "        Moon Buffer Size: " << MOONBUFFERSIZE << "        Satellite Buffer Size: " << SATELLITEBUFFERSIZE << endl;
	cout << "Store time: " << UNREALTIME_MAXDELAY << endl;
	//buffer_out.setf(ios::fixed, ios::floatfield);
	//buffer_out.precision(2);
	packet_out.setf(ios::fixed, ios::floatfield);
	packet_out.precision(2);
	hops_out.setf(ios::fixed, ios::floatfield);
	hops_out.precision(2);
	temp_result.setf(ios::fixed, ios::floatfield);
	temp_result.precision(2);
	result.setf(ios::fixed, ios::floatfield);
	result.precision(2);
	fill(isConnected[0][0], isConnected[0][0] + SIMULATOR_TIME_INT * sum_Num * sum_Num, false);
	Init_IsConnected_Hashmap();
	vector<float> result_maxbuffersize;
	for (int i = 0; i < sum_Num; ++i) {
		established_counts[i] = 0;
		established_to_which[i] = -1;
		result_maxbuffersize.push_back(0);
	}
	for (int i = 0; i < sum_Num; ++i) {
		NODE_OBJECT[i].setID(i);
		//NODE_OBJECT[i].SetMaxBandwidth();
		if (i < moon_Surface_Num) { NODE_OBJECT[i].setBufferSize(MOONBUFFERSIZE); }
		else { NODE_OBJECT[i].setBufferSize(SATELLITEBUFFERSIZE); }
	}

	for (; NOW_TIME <= SIMULATOR_TIME; ++NOW_TIME) {
		//分配带宽资源
		Caculate_SendRate();

		//检查连接状态
		for (int i = 0; i < sum_Num - 1; ++i) {
			//建立连接了 而且 物理上不通了,断开to_which，减少counts
			if (established_to_which[i] != -1 && (!isConnected[(int)NOW_TIME][i][established_to_which[i]])) {
				NODE_OBJECT[i].Delete_Connect(established_to_which[i]);
			}
		}

		//moon node
		for (int i = 0; i < moon_Node_Num; ++i) {
			NODE_OBJECT[i].GeneratePacket();
			if (i == 0 || i == 1) {
				NODE_OBJECT[i].ReceivePacket();
			}
			NODE_OBJECT[i].CheckBuffer();
			NODE_OBJECT[i].SendPacket();
		}

		//satellite
		for (int i = moon_Node_Num; i < moon_Node_Num + satellite_Node_Num; ++i) {
			NODE_OBJECT[i].ReceivePacket();
			NODE_OBJECT[i].CheckBuffer();
			NODE_OBJECT[i].SendPacket();
		}

		//earth
		for (int i = moon_Node_Num + satellite_Node_Num; i < moon_Node_Num + satellite_Node_Num + earth_Node_Num; ++i) {
			NODE_OBJECT[i].ReceivePacket();
		}

		//buffer out
		if (NOW_TIME > 43200 && NOW_TIME < 2404800) {
			for (int i = 0; i < sum_Num - 1; ++i) {
				if (result_maxbuffersize[i] < NODE_OBJECT[i].Get_BufferSizeUsed()) {
					result_maxbuffersize[i] = NODE_OBJECT[i].Get_BufferSizeUsed();
				}
			}
		}

		Output_TempResult(result_maxbuffersize);
	}
	Output_LastResult(result_maxbuffersize);

	char a;
	std::cin >> a;

	return 0;
}
