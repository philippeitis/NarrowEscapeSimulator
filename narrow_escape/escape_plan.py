import numpy as np
from .escape_utility import sphere_vol_to_r, cube_vol_to_r, calculate_delta, calculate_opt_dt
from .escape_detection import in_sphere, in_cube, passthrough_pore


def travel(delta, pa):
    p = pa.copy()
    xy = np.random.random(p.shape)
    xy = np.sqrt(xy/xy.sum() * delta) * np.random.choice([-1, +1], p.shape)
    p += xy
    return p


def escape_with_path(r, delta, dt, shape, max_steps,
                     pore_locs, pore_size, check_func):
    cur_pos = np.zeros(3)
    path = np.zeros((max_steps, 3))
    path[0] = cur_pos
    steps = 0
    while steps < max_steps:
        new_pos = travel(delta, cur_pos)
        steps = steps + 1
        while (not (check_func(new_pos, r))):
            for pd_loc in pore_locs:
                if passthrough_pore(new_pos, pd_loc, r=pore_size):
                    path[steps] = new_pos
                    return path[:steps]
            new_pos = travel(delta, cur_pos)
        cur_pos = new_pos
        path[steps] = cur_pos
    return path[:steps]


def escape(D, vol, pore_size, pore_locs,
           dt=None, seed=None, shape='sphere',
           max_steps=(int(1e7)), with_path=False):
    if dt is None:
        dt = calculate_opt_dt(pore_size, D)
    delta = calculate_delta(D, dt)
    if seed is not None:
        np.random.seed(seed)
    else:
        np.random.seed()
    max_steps = (int(1/dt) if max_steps is None else max_steps)
    check_func = in_sphere if shape == 'sphere' else in_cube
    r = sphere_vol_to_r(vol) if shape == 'sphere' else cube_vol_to_r(vol)

    if with_path:
        return escape_with_path(r, delta, dt,
                                shape, max_steps, pore_locs,
                                pore_size, check_func)
    else:
        return escape_quick(r, delta, dt,
                            shape, max_steps, pore_locs,
                            pore_size, check_func)


def escape_quick(r, delta, dt, shape, max_steps,
                 pore_locs, pore_size, check_func):
    """
    Removed tracking to optimise speed
    """
    cur_pos = np.zeros(3)
    check_func = in_sphere if shape == 'sphere' else in_cube
    steps = 0
    while steps < max_steps:
        new_pos = travel(delta, cur_pos)
        while (not (check_func(new_pos, r))):
            for pd_loc in pore_locs:
                if passthrough_pore(new_pos, pd_loc, r=pore_size):
                    return (steps+1)*dt
            new_pos = travel(delta, cur_pos)
        cur_pos = new_pos
        steps = steps + 1
    return steps*dt
