#include "Packet.h"
#include "settings.h"

float
Packet::GetPropogation_Delay() {
	float ans = 0;
	for (int i = 1; i < hops.size(); ++i) {
		if (hops[i] != sum_Num - 1) {
			ans += 0.02;
		}
		else {
			ans += 1.28;
		}
	}
	return ans;
}