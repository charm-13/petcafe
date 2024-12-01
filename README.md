# creaturecafe

**Contributors**
* Charlotte Maples, cgmaples@calpoly.edu
* Samiksha Karimbil, skarimbi@calpoly.edu
* Tracy Huang, shuan108@calpoly.edu

A backend service for an interactive fictional creature café where users can play with creatures, buy treats to feed creatures, adopt them, and more.

Persistence is added through a PostgreSQL database to store the following data:
- User info (usernames and IDs)
- User inventories (treats and gold in possession)
- Creature info (IDs, happiness and hunger levels)
- Creature types (favorite and hated treats)
- Evolution stages (max happiness and hunger levels)
- User <-> creature bonds (affinity levels and adoption status)

Different interactions with a creature satisfy different aspects of their health:
- **Playing** with a creature increases their happiness level and the user's affinity with them.
- **Feeding** a treat affects a creature's hunger and affinity level to varying degrees, depending on treat satiety and a creature's particular favorability towards a treat. 
- **Adoption** of a creature is possible after attaining an affinity level of 100 with them, which is built through repeated interactions (playing & feeding) with the creature. Adoption is per user. Adopting a creature unlocks two additional interactions:
  - **Evolving** an adopted creature increases their upper happiness and hunger level limits. The creature must currently have its happiness and hunger levels maxed out.
  - **Breeding** two adopted creatures gives the user the opportunity to add (and name!) a new creature to the café with a unique combined creature type.