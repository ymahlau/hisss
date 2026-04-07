//
// Created by mahla on 26/10/2022.
//

#ifndef BATTLESNAKECPP_BATTLESNAKE_H
#define BATTLESNAKECPP_BATTLESNAKE_H

#include <utility>
#include <deque>
#include <unordered_map>
#include <vector>
#include <list>

using namespace std;
using Coord = pair<int, int>;

void set_seed_gym(int seed);

enum DeathCause {
    DEATH_NONE = 0,
    DEATH_WALL = 1,
    DEATH_STARVATION = 2,
    DEATH_SELF = 3,
    DEATH_BODY = 4,
    DEATH_HEAD = 5,
};

struct Snake{
    Snake(int id, bool alive, int health, int length, int w, int h, int max_health, deque<Coord> spawn_pos);
    Snake(const Snake& other);
    ~Snake();
    Snake& operator=(const Snake& other);
    int id;
    bool alive;
    int health;
    int length;
    int max_health;
    int death_cause;   // DeathCause value, 0 if alive
    int death_turn;    // turn when eliminated, -1 if alive
    int killer_id;     // id of killing snake, -1 if none
    std::deque<Coord> body;
    std::vector<bool> board; //true if allocated by body
};

struct GameState{
    GameState(int w, int h, int num_snakes, int min_food, int food_spawn_chance, int init_turns_played,
              deque<deque<Coord>> snake_bodies, list<Coord> food_spawns, list<int> food_spawn_turn_values,
              bool* snake_alive, int* snake_health, int* snake_len, int* max_health,
              bool wrapped, bool royale, int shrink_n_turns, int hazard_damage, vector<bool> init_hazards);
    GameState(const GameState& other);
    ~GameState();
    GameState& operator=(const GameState& other);
    int turn;
    int w;
    int h;
    int num_snakes;
    int min_food;
    int food_spawn_chance;
    list<Coord> food;
    list<int> food_spawn_turns;
    deque<Snake*> snakes;
    bool wrapped;
    bool royale;
    int shrink_n_turns;
    int hazard_damage;
    vector<bool> hazards;
};

GameState* init(int w, int h, int num_snakes, int min_food, int food_spawn_chance, int init_turns_played,
                bool spawn_snakes_randomly, int* snake_body_lengths, int max_body_length, int* snake_bodies,
                int num_init_food, int* food_spawns, int* food_spawn_turn_values,
                bool* snake_alive, int* snake_health, int* snake_len,
                int* max_health, bool wrapped, bool royale, int shrink_n_turns, int hazard_damage, bool* init_hazards);
GameState* clone(GameState* state);
void step(GameState* state, int* actions);
void close(GameState* state);
void legal_actions(GameState* state, int snake_id, int* actions);



#endif //BATTLESNAKECPP_BATTLESNAKE_H
