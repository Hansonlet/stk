#include "load_file.h"
#include "settings.h"

void
Load_CSV_File(int i, int j) {
	char key[10] = "";
	sprintf(key, "%dto%d", i, j);
	string key_str = key;
	string str;
	str = TRACE_STR + key_str + ".csv";
	//��ʼ��ȡ
	ifstream csv_input(str, ios::in);
	string csv_str_line;//��ȡ�ļ��е�һ��
	vector<vector<float>> ans;
	getline(csv_input, csv_str_line);//��������
	while (getline(csv_input, csv_str_line)) {
		if (csv_str_line.size() < 1) { break; }
		stringstream csv_ss_line(csv_str_line);//���ļ��е�ĳһ�б��һ��string��
		char char_temp;
		float float_temp;
		int int_temp;
		string str_temp;
		//begin time
		csv_ss_line >> int_temp;
		csv_ss_line >> char_temp;
		int day1;
		csv_ss_line >> day1;
		string month1;
		csv_ss_line >> month1;
		csv_ss_line >> str_temp;
		int hour1;
		csv_ss_line >> hour1;
		csv_ss_line >> char_temp;
		int minute1;
		csv_ss_line >> minute1;
		csv_ss_line >> char_temp;
		float seconds1;
		csv_ss_line >> seconds1;
		float time1 = seconds1 + minute1 * 60 + hour1 * 60 * 60 + day1 * 24 * 60 * 60 - 100800;//1��4���ǵ�0��   - 86400;//
		//end time
		csv_ss_line >> char_temp;
		int day2;
		csv_ss_line >> day2;
		string month2;
		csv_ss_line >> month2;
		csv_ss_line >> str_temp;
		int hour2;
		csv_ss_line >> hour2;
		csv_ss_line >> char_temp;
		int minute2;
		csv_ss_line >> minute2;
		csv_ss_line >> char_temp;
		float seconds2;
		csv_ss_line >> seconds2;
		float time2 = seconds2 + minute2 * 60 + hour2 * 60 * 60 + day2 * 24 * 60 * 60 - 100800;//- 86400;//
		if (month1 == "Feb") { time1 += 31 * 24 * 60 * 60; }
		if (month2 == "Feb") { time2 += 31 * 24 * 60 * 60; }

		//��¼���
		isConnected_hashmap[key_str].push_back({ time1, time2 });
	}
}

void
Init_IsConnected(int i, int j) {
	char key[10] = "";
	sprintf(key, "%dto%d", i, j);
	string key_str = key;
	vector<vector<float>> temp = isConnected_hashmap[key_str];
	for (int m = 0; m < temp.size(); ++m) {
		for (int n = temp[m][0]; n <= temp[m][1] && n <= SIMULATOR_TIME; ++n) {
			isConnected[n][i][j] = true;
			isConnected[n][j][i] = true;
		}
	}
}

void
Init_IsConnected_Hashmap() {
	//�����û�������
	for (int i = 0; i < moon_Node_Num; ++i) {
		for (int j = moon_Node_Num; j < sum_Num - 1; ++j) {
			Load_CSV_File(i, j);
			Init_IsConnected(i, j);
		}
	}
	//���ǵ�����
	for (int i = moon_Node_Num; i < moon_Node_Num + satellite_Node_Num; ++i) {
		int j = sum_Num - 1;
		Load_CSV_File(i, j);
		Init_IsConnected(i, j);
	}
	//����ֱ��
	Load_CSV_File(0, sum_Num - 1);
	Init_IsConnected(0, sum_Num - 1);
	Load_CSV_File(1, sum_Num - 1);
	Init_IsConnected(1, sum_Num - 1);
	//�ɴ����»�ͨ��(���)վ
	for (int i = moon_Surface_Num; i < moon_Node_Num; ++i) {
		Load_CSV_File(0, i);
		Init_IsConnected(0, i);
	}
}