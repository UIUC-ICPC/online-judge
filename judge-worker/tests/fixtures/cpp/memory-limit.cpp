#include <iostream>
#include <vector>

int main() {
  std::vector<char> vec(2'000'000'000, 1);
  int sum = 0;
  for (int i = 0; i < vec.size(); ++i) {
    sum += vec[i];
  }
  std::cout << sum << std::endl;
}
