create table
  public.treats (
    sku text not null,
    name text not null,
    satiety integer not null default 0,
    price integer not null default 0,
    constraint treats_pkey primary key (sku),
    constraint treats_name_key unique (name),
    constraint treats_sku_key unique (sku)
  ) tablespace pg_default;

create table
  public.creature_types (
    id bigint generated by default as identity not null,
    type text not null,
    fav_treat text not null,
    hated_treat text not null,
    constraint creature_types_pkey primary key (id),
    constraint creature_types_id_key unique (id),
    constraint creature_types_type_key unique (
      type
    ),
    constraint creature_types_fav_treat_fkey foreign key (fav_treat) references treats (sku),
    constraint creature_types_hated_treat_fkey foreign key (hated_treat) references treats (sku)
  ) tablespace pg_default;

create table
  public.creatures (
    id bigint generated by default as identity not null,
    name text not null,
    type text not null,
    happiness integer not null default 0,
    health integer not null default 0,
    hunger integer not null default 100,
    constraint creatures_pkey primary key (id),
    constraint creatures_name_key unique (name),
    constraint creatures_type_fkey foreign key (
      type
    ) references creature_types (
      type
    )
  ) tablespace pg_default;

create table
  public.users (
    id bigint generated by default as identity not null,
    username text not null,
    gold integer not null default 0,
    constraint users_pkey primary key (id),
    constraint users_username_key unique (username)
  ) tablespace pg_default;
  INSERT INTO "public"."users" ("id", "username", "gold") VALUES ('1', 'test', '0');

create table
  public.users_inventory (
    id bigint generated by default as identity not null,
    user_id bigint not null,
    treat_sku text not null,
    quantity integer not null default 0,
    creatures text null,
    constraint users_inventory_pkey primary key (id),
    constraint users_inventory_creatures_fkey foreign key (creatures) references creatures (name),
    constraint users_inventory_treat_sku_fkey foreign key (treat_sku) references treats (sku) on update cascade on delete cascade,
    constraint users_inventory_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade
  ) tablespace pg_default;
  INSERT INTO "public"."users_inventory" ("id", "user_id", "treat_sku", "quantity") VALUES ('1', '1', 'CLOUD_CANDY', '1'), ('2', '1', 'HONEY', '1');

create table
  public.user_creature_connection (
    user_id bigint not null,
    creature_id bigint not null,
    affinity integer not null default 0,
    constraint user_creature_connection_pkey primary key (user_id, creature_id),
    constraint user_creature_connection_creature_id_fkey foreign key (creature_id) references creatures (id) on update cascade on delete cascade,
    constraint user_creature_connection_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade
  ) tablespace pg_default;

  create table
  public.user_adoptions (
    user_id bigint generated by default as identity not null,
    creature_id bigint not null,
    constraint user_adoptions_pkey primary key (user_id, creature_id),
    constraint user_adoptions_creature_id_fkey foreign key (creature_id) references creatures (id),
    constraint user_adoptions_user_id_fkey foreign key (user_id) references users (id) on delete cascade
  ) tablespace pg_default;

create table
  public.carts (
    id bigint generated by default as identity not null,
    user_id bigint not null,
    created_at timestamp with time zone not null default now(),
    constraint carts_pkey primary key (id),
    constraint carts_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade
  ) tablespace pg_default;

create table
  public.carts_items (
    cart_id bigint not null,
    item_sku text not null,
    quantity integer not null default 0,
    constraint carts_items_pkey primary key (cart_id, item_sku),
    constraint carts_items_cart_id_fkey foreign key (cart_id) references carts (id) on update cascade on delete cascade,
    constraint carts_items_item_sku_fkey foreign key (item_sku) references treats (sku) on update cascade on delete cascade
  ) tablespace pg_default;
