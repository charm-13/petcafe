# Example workflow
Pet Cafe User Viewing Example Flow <br>
A new user creates their account with username "dragonluvr5" and is assigned id `1`. They want to view the list of creatures that are available to interact with. 
They view the list of pets and then check their own inventory to see what they have. They realize they have 0 gold and 0 treats and on top of that, they hate 
the names of the pets!! They become violently upset at the situation, so they decide to delete their account.

# Testing results
Start by calling `POST /users/create` and pass in "dragonluvr5". They're assigned id `1`:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.

Then they call `GET /inventory/1` to view their inventory:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
   
Then call `GET /creatures/1` to view the list of available creatures and their current affinity with them:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
   
Finally, they call `DELETE /users/1/delete` to delete their account:
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
