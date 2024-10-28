# Example workflow
Pet Cafe User Viewing Example Flow <br>
A new user creates their account with username "dragonluvr5" and is assigned id `1`. They want to view the list of creatures that are available to interact with. 
They view the list of pets and then check their own inventory to see what they have. They realize they have 0 gold and 0 treats and on top of that, they hate 
the names of the pets!! They become violently upset at the situation, so they decide to delete their account.

# Testing results
**Start by calling `POST /users/create` and pass in "dragonluvr5". They're assigned id `1`:**
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

**Then they call `GET /inventory/1` to view their inventory:**
1. curl -X 'POST' \
  'http://127.0.0.1:3000/users/1/inventory' \
  -H 'accept: application/json' \
  -H 'access_token: oi1i2O9tZgaExzgC' \
  -d ''
2. {"name": "dragonluvr5", <br>
  "treats": ["CLOUD_CANDY", "HONEY"], <br>
  "gold": 0, <br>
  "pets": ["Blaze", "Whiskaroo"]}
   
**Then call `GET /creatures/1` to view the list of available creatures and their current affinity with them:**
1. curl -X 'POST' \
  'http://127.0.0.1:3000/users/1/creatures/' \
  -H 'accept: application/json' \
  -H 'access_token: oi' \
  -d ''
2. [{"name": "Whiskaroo", "type": "silly_cat", "affinity": 100}, <br>
  {"name": "Rumbull", "type": "fighter_cow", "affinity": 0}, <br>
  {"name": "Spectrip", "type": "sea_ghost", "affinity": 0}, <br>
  {"name": "Mindara", "type": "psychic_unicorn", "affinity": 0}, <br>
  {"name": "Flutterbop", "type": "flying_bug", "affinity": 0}, <br>
  {"name": "Thornvyne", "type": "grass_dragon", "affinity": 0}, <br>
  {"name": "Shellwater", "type": "water_turtle", "affinity": 0}, <br>
  {"name": "Infernyx", "type": "fire_lizard", "affinity": 0}, <br>
  {"name": "Nibbly", "type": "silly_cat", "affinity": 0}, <br>
  {"name": "Brawlow", "type": "fighter_cow", "affinity": 0}, <br>
  {"name": "Mystara", "type": "psychic_unicorn", "affinity": 0}, <br>
  {"name": "Shocuff", "type": "electric_sheep", "affinity": 0}, <br>
  {"name": "Flyka", "type": "flying_bug", "affinity": 0}, <br>
  {"name": "Fayblossom", "type": "fluffy_fairy", "affinity": 0}, <br>
  {"name": "Grumblevine", "type": "grass_dragon", "affinity": 0}, <br>
  {"name": "Aquaquel", "type": "water_turtle", "affinity": 0}, <br>
  {"name": "Zap E. Wool", "type": "electric_sheep", "affinity": 0}, <br>
  {"name": "Blaze", "type": "fire_lizard", "affinity": 100}, <br>
  {"name": "Haunter Glow", "type": "sea_ghost", "affinity": 0}, <br>
  {"name": "Puffilia", "type": "fluffy_fairy", "affinity": 0}]
   
Finally, they call `DELETE /users/1/delete` to delete their account:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
