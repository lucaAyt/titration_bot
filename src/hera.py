import os
import json

from .libs import titration as titr

dict_titrants_exps = {}                 # storage of titrant use in titration experiment
dict_titrations_exps = {}               # storage of titration objects which are associated with experiment

# Load config json
cnfg_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
cnfg = json.load(open(cnfg_path))


def initialize_titrations(exp_: list[str]) -> None:
    """
    Used to initialise titration experiments from a list of experiment names provided
    and the corresponding parameters stipulated in the config for each experiment name.
    :param exp_: list of titration experiments to analyse
    :return: n.a.
    """

    global dict_titrants_exps, dict_titrations_exps
    # TODO: Assert exp_ is dict

    # Run through each experiment in config
    for titration_exp in cnfg['titrations']:

        # Look up interested titration experiments
        if titration_exp.get('name') in exp_:
            exp_name = titration_exp.get('name')
            titrants = titration_exp.get('titrants')

            # Create titrants used for this experiment and store in dictionary for global use
            titrants_objs = []
            for titrant in titrants:
                titrants_objs.append(titr.titrant(**titrant))
            dict_titrants_exps[exp_name] = titrants_objs

            # Create Titration objects based on titration specified and the titrants used for experiment
            # Sort titrations according to rank
            exp_titrations = sorted(titration_exp.get('tits'), key=lambda x: x['titration_rank']) \
                if len(titration_exp.get('tits')) > 1 else titration_exp.get('tits')
            titrations_objs = []

            # Store init_volume
            init_volume = 0

            for i, titration in enumerate(exp_titrations):
                exp_titrants = dict_titrants_exps[exp_name]

                # Get host and guest titrant objects
                host = [*filter(lambda titrant_x: titrant_x.name == titration['host_name'], exp_titrants)][0]
                guest = [*filter(lambda titrant_x: titrant_x.name == titration['guest_name'], exp_titrants)][0]

                # Construct initial titration
                if i == 0:

                    # Update init_volume - can only be updated on first titration
                    init_volume = titration['init_volume']

                    # Create titration object with all parameters and store
                    titration_obj = titr.Titration(host, guest, init_volume, titration['tit_volume'],
                                                   titration['num_tit'], titration['titration_rank'],
                                                   titr_volume_array=titration.get('tit_volume_array', []))

                    titration_obj.construct_gh_titration()
                    titrations_objs.append(titration_obj)

                # Construct subsequent titration based on prior
                else:

                    # Get starting parameters from prior titration - host mol is adapted if host is a complex or not
                    curr_volume = titrations_objs[i - 1].df_params.volume_total.values[-1] * 1e3  # mL
                    mol_host = titrations_objs[i - 1].host_mol_init / host.order_complex \
                        if host.order_complex != 0 else titrations_objs[i - 1].host_mol_init  # mol
                    conc_host = mol_host / (curr_volume / 1e3)  # M

                    # Reinitilaise or update inSitu titrants (host) provided new volume and mol plus overwrite
                    host_attrs = {**vars(host), 'mol': mol_host, 'volume': curr_volume, 'conc': conc_host}
                    host = titr.titrant(**host_attrs)

                    # TODO: Overwrite titrant object stored in dict_titrants_exps to avoid possible bugs
                    # Create titration object with all parameters and store
                    titration_obj = titr.Titration(host, guest, init_volume, titration['tit_volume'],
                                                   titration['num_tit'], titration['titration_rank'],
                                                   titr_volume_array=titration.get('tit_volume_array', []),
                                                   curr_volume=curr_volume)

                    titration_obj.construct_gh_titration()
                    titrations_objs.append(titration_obj)

            # Store titration objects in accordance with name of experiment
            dict_titrations_exps[exp_name] = (titrations_objs, len(titration_exp.get('tits')))


# if __name__ == '__main__':
#     titration_experiments = ['LUB160']
#     initialize_titrations(titration_experiments)



