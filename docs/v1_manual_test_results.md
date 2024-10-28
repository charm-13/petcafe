# Example workflow
Pet Cafe User-Pet Interaction Example Flow: <br>
The user identified by id 475 has the goal of adopting all creatures available, and strategizes by prioritizing interactions with the ones they have the lowest affinity with. They check their affinity levels with the available creatures and decide to interact with the creature with id 25, who has an affinity level 20 with the user. They feed the creature RAZZ_BERRYs and play with it. Then, they adopt the creature because they have enough affinity with it.

# Testing results
Call `POST /users/475/creatures` to view the creatures:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

Call `GET /users/475/creatures/25/stats` to get the creature's current hunger and happiness levels:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
   
Feed the creature using a treat by calling `POST /users/475/creatures/25/feed/RAZZ_BERRY`:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
   
Play with the creature by calling `POST /users/475/creatures/25/play`:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

Call `POST /users/475/creatures/25/adopt` to adopt that creature:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
