# Example workflow
Pet Cafe User-Pet Interaction Example Flow:
The user identified by id 475 has the goal of adopting all creatures available, and strategizes by prioritizing interactions with the ones they have the lowest affinity with. They check their affinity levels with the available creatures, and decide to interact with the creature with id 25, who has affinity level 20 with the user. Then, they adopt the creature because they see that they have enough affinity with it. To satisfy the needs of the creature they do the following.

# Testing results
Call POST /creatures/475 to view the creatures:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

Call GET /creatures/475/stats and pass in a creature_id of 25 to get the creature's current hunger and happiness levels.
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
   
Feed the creature using a treat by calling POST /creatures/475/feed and passing in creature_id and treat_id.
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
   
Play with the creature by calling POST /creatures/475/play and passing in the creature_id.
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

Check the creature's updated happiness and hunger levels using GET /creatures/475/stats again.
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

Call POST/creatures/475/adopt and pass in a creature_id of 25 to adopt that creature.
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
