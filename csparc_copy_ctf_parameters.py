import argparse
import numpy as np
from cryosparc.tools import CryoSPARC

parser = argparse.ArgumentParser(description='A simple script for cryoSPARC to copy CTF parameters from one job and apply them to another job. Useful if your project has multiple proteins but one is much higher resolution than the other.')
parser.add_argument('project', metavar='project_id', type=str,
                    help='The project ID of your cryoSPARC dataset, e.g. P14')
parser.add_argument('workspace', metavar='workspace_id', type=str,
                    help='The workspace ID of your cryoSPARC dataset, e.g. W2')
parser.add_argument('job', metavar='job_id', type=str,
                    help='The job number of your CTF refinement job, e.g. J100')
parser.add_argument('particles', metavar='particles_id', type=str,
                    help='The job number of the particles you wish to apply CTF parameters to, e.g. J200')
args = parser.parse_args()


cs = CryoSPARC(
    license="id-goes-here",
    host="host",
    base_port=39000,
    email="email@email.com",
    password="password",
)

# Substitute with project and job details:
puid = args.project
wuid = args.workspace
ref_particles_juid = args.job
ref_particles_output = "particles"
new_particles_juid = args.particles
new_particles_output = "particles"

# Setup job
job = cs.create_external_job(puid, wuid, title=f"{new_particles_juid} CTF Refined Particles")
job.connect("ref_particles", ref_particles_juid, ref_particles_output, slots=["ctf"])
job.connect("new_particles", new_particles_juid, new_particles_output, slots=["ctf"])
job.add_output("particle", "particles", slots=["ctf"], passthrough="new_particles")

# Run job
with job.run():
    ref_particles = job.load_input("ref_particles", slots=["ctf"])
    new_particles = job.load_input("new_particles", slots=["ctf"])

    for exp_group, ref_parts in ref_particles.split_by("ctf/exp_group_id").items():
        mask = new_particles['ctf/exp_group_id'] == exp_group
        for field in [  # add/remove fields here as needed
            'ctf/accel_kv',
            'ctf/cs_mm',
            'ctf/df_angle_rad',
            'ctf/df1_A',
            'ctf/df2_A',
            'ctf/phase_shift_rad',
            'ctf/anisomag',
            'ctf/shift_A',
            'ctf/tilt_A',
            'ctf/trefoil_A',
            'ctf/tetra_A'
        ]:
            new_particles[field][mask] = ref_parts[field][0]

    job.save_output("particles", new_particles)