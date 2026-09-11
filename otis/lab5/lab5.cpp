#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>

using namespace std;

bool is_higher(vector<int> expert_rating, int first, int second)
{
    for(auto alt : expert_rating){
        if(alt == first)
            return true;
        if(alt == second)
            return false;
    }
}

void validate_input(vector<int> alt_keys, int key){
    for(auto k : alt_keys){
        if(k == key)
            return;
    }
    throw invalid_argument("Unappropriated key for the alternative!");
}

int main()
{
    vector<string> alternatives;
    alternatives.push_back("Maintain strict records of blank forms issued to universities");
    alternatives.push_back("Introduce a new watermark system");
    alternatives.push_back("Require hiring managers to verify the authenticity of a diploma");
    int alt_num = alternatives.size();

    vector<int> alt_keys;
    cout << "Alternatives" << endl;
    for(int i = 0; i < alt_num; i++){
        alt_keys.push_back(i + 1);
        cout <<"Key " << i + 1 << " -- " << alternatives[i] << endl;
    }
    cout << endl;

    int exp_num;
    cout << "Enter amount of experts: ";
    cin >> exp_num;
    vector<vector<int>> experts_range(alt_num, vector<int>(exp_num));
    for (int i = 0; i < exp_num; i++)
    {
        cout << endl << "Expert " << i + 1 << endl;
        for (int j = 0; j < alt_num; j++)
        {
            int alt_key;
            cout << "At " << j + 1 << " place put the alternative with key: ";
            cin >> alt_key;
            try{
                validate_input(alt_keys, alt_key);
            }
            catch (const std::invalid_argument& e) {
                cerr << e.what() << endl;
                cout << "Try again" << endl;
                j--;
                continue;
            }
            experts_range[i][j] = alt_key;
        }
    }

    int winners = 0;
    string winner_alt;
    for (int i = 0; i < alt_num; i++)
    {
        bool is_winner = true;
        for (int j = 0; j < alt_num; j++)
        {
            if(j == i)
                continue;
            int count = 0;
            for (auto expert_rating : experts_range) 
            {
                count += static_cast<int>(is_higher(expert_rating, alt_keys[i], alt_keys[j]));
            }
            float x = exp_num / 2.0;
            if (count < x) {
                is_winner = false;
                break;
            }
        }
        if(is_winner){
            winner_alt = alternatives[i];
            winners++;
        }
    }

    if(winners == 1)
        cout << "Winner: " << winner_alt << endl;
    else cout << "Winner don't exist" << endl;
    return 0;
}