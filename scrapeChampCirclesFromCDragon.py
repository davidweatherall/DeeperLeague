import requests
import os

patch = '14.1'
version = patch + '.1'

champions_static = f'http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json'

champions = requests.get(champions_static).json()['data']

champ_names = list(champions.keys())

os.makedirs('./champions', exist_ok=True)

# loop through champ names

for champ_name in champ_names:
  lower_case_champ_name = champ_name.lower()
  champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/{lower_case_champ_name}/hud/{lower_case_champ_name}_circle.png'
  champ_path_opt_2 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/{lower_case_champ_name}/hud/{lower_case_champ_name}_circle_0.png'

  if(lower_case_champ_name == 'anivia'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/anivia/hud/cryophoenix_circle.png'

  if(lower_case_champ_name == 'blitzcrank'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/blitzcrank/hud/steamgolem_circle.png'

  if(lower_case_champ_name == 'briar'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/briar/hud/briar_circle_0.briar.png'

  if(lower_case_champ_name == 'chogath'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/chogath/hud/greenterror_circle.png'

  if(lower_case_champ_name == 'jax'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/jax/hud/jax_circle_0.jaxupdate.png'

  if(lower_case_champ_name == 'orianna'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/orianna/hud/oriana_circle.png'

  if(lower_case_champ_name == 'rammus'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/rammus/hud/armordillo_circle.png'

  if(lower_case_champ_name == 'shaco'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/shaco/hud/jester_circle.png'

  if(lower_case_champ_name == 'syndra'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/syndra/hud/syndra_circle_0.pie_c_13_24.png'

  if(lower_case_champ_name == 'zilean'):
    champ_path_opt_1 = f'https://raw.communitydragon.org/{patch}/game/assets/characters/zilean/hud/chronokeeper_circle.png'

  response = requests.get(champ_path_opt_1)
  if response.status_code != 200:
    response = requests.get(champ_path_opt_2)

  if response.status_code != 200:
    print("failed to get champ circle for {0}".format(champ_name))
    continue

  # make a dir for the champ

  os.mkdir('./champions/{0}'.format(champ_name))

  with open('./champions/{0}/1.png'.format(champ_name), 'wb') as f:
    f.write(response.content)

  if lower_case_champ_name == 'kayn':
    assasin_image_path = f'https://raw.communitydragon.org/{patch}/game/assets/characters/kayn/hud/kayn_ass_circle.png'
    response = requests.get(assasin_image_path)
    if(response.status_code != 200):
      print("Failed to get kayn assasin form image")
    else:
      with open('./champions/{0}/2.png'.format(champ_name), 'wb') as f:
        f.write(response.content)
      
      
    darkin_image_path = f'https://raw.communitydragon.org/{patch}/game/assets/characters/kayn/hud/kayn_slay_circle.png'
    response = requests.get(darkin_image_path)
    if(response.status_code != 200):
      print("Failed to get kayn darkin form image")
    else:
      with open('./champions/{0}/3.png'.format(champ_name), 'wb') as f:
        f.write(response.content)
      
  if lower_case_champ_name == 'gnar':
    megagnar_path = f'https://raw.communitydragon.org/{patch}/game/assets/characters/gnarbig/hud/gnarbig_circle.png'
    response = requests.get(megagnar_path)
    if(response.status_code != 200):
      print("Failed to get mega gnar form image")
    else:
      with open('./champions/{0}/2.png'.format(champ_name), 'wb') as f:
        f.write(response.content)

  if lower_case_champ_name == 'yuumi':
    yuumi_path = 'https://raw.communitydragon.org/13.15/game/assets/characters/yuumi/hud/yuumi_circle_0.png'
    response = requests.get(yuumi_path)
    if(response.status_code != 200):
      print("Failed to get yuumi form image")
    else:
      with open('./champions/{0}/2.png'.format(champ_name), 'wb') as f:
        f.write(response.content)

  print(champ_name)