import simpy

class MammoClinic(object):
    def __init__(self, env, num_checkin_staff, num_public_wait_room,
                 num_change_room, num_gowned_wait_room,
                 num_scanner, num_us_machine, num_radiologist, rg, num_consent_staff=None):
        # simulation env
        self.env = env
        self.rg = rg

        # create list to hold timestamps dictionaries (one per pt)
        self.timestamps_list = []

        # creat resources
        self.checkin_staff = simpy.Resource(env, num_checkin_staff)
        self.public_wait_room = simpy.Resource(env, num_public_wait_room)
        self.consent_staff = simpy.Resource(env, num_consent_staff)
        self.change_room = simpy.Resource(env, num_change_room)
        self.gowned_wait_room = simpy.Resource(env, num_gowned_wait_room)
        self.scanner = simpy.Resource(env, num_scanner)
        self.us_machine = simpy.Resource(env, num_us_machine)
        self.radiologist = simpy.Resource(env, num_radiologist)

    def pt_checkin(self, patient):
        yield self.env.timeout(self.rg.normal(0.05, 0.01))

    def use_public_wait_room(self, patient):
        yield self.env.timeout(self.rg.normal(0.17, 0.034))

    def consent_patient(self, patient):
        yield self.env.timeout(self.rg.normal(0.17, 0.034))

    def use_change_room(self, patient):
        yield self.env.timeout(self.rg.normal(0.03, 0.006))

    def use_gowned_wait_room(self, patient):
        yield self.env.timeout(self.rg.normal(0.017, 0.0034))

    def get_screen_mammo(self, patient):
        yield self.env.timeout(self.rg.normal(0.17, 0.034))

    def get_dx_mammo(self, patient):
        yield self.env.timeout(self.rg.normal(0.50-0.083, 0.0834))

    def get_dx_us(self, patient):
        yield self.env.timeout(self.rg.normal(0.50-0.083, 0.0834))

    def get_us_guided_bx(self, patient):
        yield self.env.timeout(self.rg.normal(0.75, 0.15))

    def get_mammo_guided_bx(self, patient):
        yield self.env.timeout(self.rg.normal(0.75, 0.15))

    def get_screen_us(self, patient):
        yield self.env.timeout(self.rg.normal(0.25, 0.05))

    def get_mri_guided_bx(self, patient):
        yield self.env.timeout(self.rg.normal(0.5, 0.1))

    def rad_review(self, patient):
        yield self.env.timeout(self.rg.normal(0.083, 0.017))

class MammoClinic_1SS(object):
    def __init__(self, env, num_checkin_staff, num_public_wait_room,
                 num_change_room,
                 num_gowned_wait_room,
                 num_scanner, num_us_machine, num_radiologist, num_radiologist_same_day, rad_change, rad_change_2, rg,
                 num_consent_staff=None):
        # simulation env
        self.env = env
        self.rg = rg

        # create list to hold timestamps dictionaries (one per pt)
        self.timestamps_list = []

        # creat resources
        self.checkin_staff = simpy.Resource(env, num_checkin_staff)
        self.public_wait_room = simpy.Resource(env, num_public_wait_room)
        self.consent_staff = simpy.Resource(env, num_consent_staff)
        self.change_room = simpy.Resource(env, num_change_room)
        self.gowned_wait_room = simpy.Resource(env, num_gowned_wait_room)
        self.scanner = simpy.Resource(env, num_scanner)
        self.us_machine = simpy.Resource(env, num_us_machine)
        self.radiologist = simpy.Resource(env, num_radiologist)
        if rad_change or rad_change_2:
            self.radiologist_same_day = simpy.Resource(env, num_radiologist_same_day)

    def pt_checkin(self, patient):
        yield self.env.timeout(self.rg.normal(0.05, 0.01))

    def use_public_wait_room(self, patient):
        yield self.env.timeout(self.rg.normal(0.17, 0.034))

    def consent_patient(self, patient):
        yield self.env.timeout(self.rg.normal(0.17, 0.034))

    def use_change_room(self, patient):
        yield self.env.timeout(self.rg.normal(0.03, 0.006))

    def use_gowned_wait_room(self, patient):
        yield self.env.timeout(self.rg.normal(0.017, 0.0034))

    def get_screen_mammo(self, patient):
        yield self.env.timeout(self.rg.normal(0.17, 0.034))

    def get_dx_mammo(self, patient):
        yield self.env.timeout(self.rg.normal(0.50-0.083, 0.0834))

    def get_dx_us(self, patient):
        yield self.env.timeout(self.rg.normal(0.50-0.083, 0.0834))

    def get_us_guided_bx(self, patient):
        yield self.env.timeout(self.rg.normal(0.75, 0.15))

    def get_mammo_guided_bx(self, patient):
        yield self.env.timeout(self.rg.normal(1.25, 0.25))

    def get_ai_assess(self, patient):
        yield self.env.timeout(self.rg.normal(0.25, 0.05))

    def get_screen_us(self, patient):
        yield self.env.timeout(self.rg.normal(0.25, 0.05))

    def get_mri_guided_bx(self, patient):
        yield self.env.timeout(self.rg.normal(0.5, 0.1))

    def rad_review(self, patient):
        yield self.env.timeout(self.rg.normal(0.083, 0.017))

