# Chess

## Setup Instructions

1. Run the following command in the terminal to install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the following command to compile the code (Optional, accounts for ~3x speedup):
    ```bash
    python build/setup.py build_ext --inplace
    ```
> **Note:** Unless you see a message that says "error", you can ignore any error-looking output.

## Usage Instructions - The Main Program

- Run the following command to start the game:
    ```bash
    python main.py
    ```
### Main Menu Options

 - **Options** - Switch to the options menu.
 - **Human** - Play against yourself or pass the computer between you and your friend.
 - **Play White** - Play against the computer as white.
 - **Play Black** - Play against the computer as black.
 - **AI vs AI** - Play against the computer as white and black.
 - **Deep Test** - Play the one bot against another bot in 1000 games to see which is better.

### Options Menu Options

 - **Main Menu** - Return to the main menu.
 - **BotVx** - Click to cycle through the bots to play against (white).
 - **BotVx** - Click to cycle through the bots to play against (black).
 - **Normal/Test** - Click to switch between normal and test mode.

## Usage Instructions - `benchmark.py`

In `if __name == '__main__':`, you can toggle between `deep_test()` and `main()`.

### `main()`

 - Used to time one function against another.
 - Can change functions in the `bechmark()` function.

### `deep_test()`

 - Used to get the average time it takes for bot or RNG to take a turn or play a game.
 - Can change how long the test is and what is playing the game in `test()` and `deep_test()`.

