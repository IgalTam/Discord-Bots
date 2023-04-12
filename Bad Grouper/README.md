# Bad Grouper

### Overview
This bot is designed to automate server tasks involving tedious administrative actions. This includes creating multiple channels at once, removing multiple channels at once, and assigning a role to multiple members at once. Additionally, the ```gmaker``` and ```rmaker``` Cogs allow for the archiving and cloning of guild channels and roles.

### Special Notes
1) For guild safety, all commands require adminstrator permissions to use.
2) ```mult```: This is a complex but flexible UNIX-style command that can perform multiple operations simultaneously. Due to the variable quantity of parameters that can be inputted to the command, it is not supported by slash commands. As such, it must be run with the command prefix ```/*/```. See the command ```mult_help``` for more information on using ```mult```.
3) ```mtr``` and ```rmr``` are commands that share the same compatibility isseus as ```mult```, and must also be called using the command prefix syntax.

### Command List

#### Main Suite (badgrouper.py)
```make <num> <name> [role_make]```: Creates _num_ Category channels with name _name_, each with a corresponding text and voice channel. The optional *role_make* boolean will also create roles that provide exclusive access to their corresponding channel.<br />
```clean <name>```: Deletes all channels in the guild created with ```make``` that have the name _name_.<br />
```clean_spec <name> [cat]```: Deletes all channels in the category _cat_ with name _name_ (not necessarily made with ```make```). If _cat_ is not provided, ```clean_spec``` will search in the outermost scope of channels.<br />
```mtr <role> <user1, user2, ...>```: Assigns the guild role _role_ to all users associated with input usernames/nicknames.<br />
```rmr <role> <user1, user2, ...>```: Removes the guild role _role_ from all users associated with input usernames/nicknames.<br />
```make_role <name>```: Creates a new role with name _name_ and without permissions.<br />
```rem_role <name>```: Removes all roles with name _name_ from the guild.<br />
```mult <see mult_help for syntax>```: Complex multipurpose command capable of running each of the previous commands with one call. Order of operations: 1. ```clean```, 2. ```rem_role```, 3. ```make_role```, 4. ```make```, 5. either ```mtr``` or ```rmr```. <br />
```mult_help```: Explains the syntax for mult (akin to a UNIX man page)

##### Gmaker Cog (gmaker.py)
```gmake <infile>```: Reconstructs the guild channel hierarchy contained in the input text file (ideally one created with ```gmakesnap``` or ```gmakeinter```).
```cgmake <infile>```: Same functionality as ```gmake```, but wipes the existing guild channel hierarchy before creating new channels (requires guild owner privileges).
```gmakesnap```: Saves the guild channel hierarchy of the calling message's guild as a text file.
```gmakeinter```: Interactive process used for manually constructing a guild channel hierarchy text file.

##### Rmaker Cog (rmaker.py)
```rmake <infile>```: Reconstructs the guild roles contained in the input text file (ideally one created with ```rmakesnap``` or ```rmakeinter```).
```crmake <infile>```: Same functionality as ```rmake```, but wipes the existing guild roles before creating new roles (requires guild owner privileges).
```rmakesnap```: Saves the roles of the calling message's guild as a text file (saves all properties except role distribution to members).
```rmakeinter```: Interactive process used for manually constructing a guild role text file.