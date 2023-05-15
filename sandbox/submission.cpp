#include <bits/stdc++.h>
#define int long long
#define endl "\n"
using namespace std;

int dp[1000005];
bool num[1000005];

signed main() {
	ios::sync_with_stdio(false); cin.tie(0);
	int n, m, k;
	cin >> n >> m >> k;
	vector<int> count(k);
	vector<int> price(k);
	for (int i = 0; i < k; i++) cin >> count[i];
	for (int i = 0; i < k; i++) cin >> price[i];
	for (int i = 0; i <= n; i++) {
		dp[i] = 8e18;
		num[i] = false;
	}
	for (int i = 0; i < m; i++) {
		int tmp;
		cin >> tmp;
		num[tmp] = true;
	}
	dp[0] = 0;
	for (int i = 1; i <= n; i++) {
		if (!num[i]) dp[i] = dp[i-1];
		else {
			for (int j = 0; j < k; j++) {
		            dp[i] = min(dp[i], dp[max(i - count[j], (long long)0)] + price[j]);
			}
		}
	}
	cout << dp[n] << endl;
}