import pandas as pd
import numpy as np

from dataclasses import dataclass, field

@dataclass
class Titrant:
    """
    Dataclass used to create titrants for titrations
    """

    # TODO: Add density
    type_tit: str  # Host, Guest
    name: str
    molecular_weight: float  # g/mol
    mass: float  # mg
    volume: float  # mL
    mol: float = 0
    conc: float = 0
    order_complex: int = 0
    dilute: list[list[float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.mol == 0 and self.conc == 0 and self.volume != 0:
            self.mol = self.mass / 1000 / self.molecular_weight    # mol
            self.conc = self.mol / (self.volume / 1000)            # M

        # TODO: Would be nice to add a test for this.
        elif self.conc != 0 and self.mol == 0:
            self.mol = self.conc * (self.volume / 1e3)      # mol
            self.mass = self.mol * self.molecular_weight    # g

        if self.dilute:
            for dil in self.dilute:
                self.dilution(*dil)

    def dilution(self, v1: float, v2: float) -> None:
        # Unit conversion
        v1 = v1 / 1000  # mL to dm3
        v2 = v2 / 1000  # mL to dm3

        self.conc = self.conc * v1 / v2

        # auto-overwrite volume, moles to diluted solution
        self.mol = self.conc * v2
        self.volume = v2 * 1000  # dm3 to mL


class Titration:
    """
    Titration object used to contain all parameters of a specific host-guest titration.
    There can be multiple titrations per experiment.
    """

    # TODO: ranks should be int
    def __init__(self, host: Titrant, guest: Titrant, init_volume: float, titr_volume: float, num_titr: float,
                 rank: float, titr_volume_array: list[float], curr_volume=None):
        assert host.type_tit.lower() == 'host' or 'inSitu_host', 'Argument not of type Host'
        assert guest.type_tit.lower() == 'guest', 'Argument not of type Guest'
        if titr_volume_array:
            assert len(titr_volume_array) == num_titr, 'Number of titrations not matched with sequence given.'

        self.host = host
        self.guest = guest

        self.init_volume = init_volume  # mL
        self.curr_volume = curr_volume if curr_volume else init_volume  # mL
        self.tit_volume = titr_volume  # µL
        self.num_tit = num_titr
        self.tit_volume_array = titr_volume_array  # µL
        self.rank = rank

        # All parameters of titration to be populated in dataframe
        self.df_params = pd.DataFrame()

    def construct_gh_titration(self) -> None:
        """
        Maps all parameters of the designed titration to a dataframe
        :return: n.a
        """

        # TODO: Ensure guest is titrated and host is init sol

        indx = np.arange(self.num_tit + 1)
        vol_cumsum = np.insert(np.cumsum(self.tit_volume_array), 0, 0) if self.tit_volume_array else []
        volume_tot = [*map(lambda x: (x * self.tit_volume) / 1e6 + self.curr_volume / 1e3, indx)] \
            if not self.tit_volume_array else [*map(lambda x: vol_cumsum[x] / 1e6 + self.curr_volume / 1e3, indx)]
        vol_change = [*map(lambda x: round((x - self.init_volume / 1e3) * 1e6, 2), volume_tot)]

        self.host_mol_init = self.host.conc * (self.curr_volume / 1e3)

        data = {
            'volume_total': volume_tot,
            'volume_change': vol_change,
            'host_conc': [*map(lambda x: self.host_mol_init / x, volume_tot)],
            'host_mol': self.host_mol_init,
            'guest_mol': [*map(lambda x: (x * self.tit_volume) / 1e6 * self.guest.conc, indx)] \
                if not self.tit_volume_array else [*map(lambda x: vol_cumsum[x] / 1e6 * self.guest.conc, indx)],
            'guest_name': self.guest.name,
            'host_name': self.host.name,
            'rank': self.rank
        }

        self.df_params = pd.DataFrame(index=indx, data=data)
        self.df_params['guest_conc'] = self.df_params.guest_mol / self.df_params.volume_total
        self.df_params['g_h_mol'] = self.df_params.guest_mol / self.df_params.host_mol
        self.df_params['g_h'] = self.df_params.guest_conc / self.df_params.host_conc
