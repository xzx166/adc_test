# coding=utf-8

import os

from poco.utils.vector import Vec2


def track_sampling(track, accuracy=0.002):
    # accuracy： 采样精度，都是归一化坐标系
    if len(track) <= 1:
        return track

    total_distance = 0.0
    for i in range(len(track) - 1):
        p0 = Vec2(track[i])
        p1 = Vec2(track[i + 1])
        total_distance += (p1 - p0).length

    sample_points = []
    for i in range(len(track) - 1):
        p0 = Vec2(track[i])
        p1 = Vec2(track[i + 1])
        d = p1 - p0
        seg_length = d.length
        d = (p1 - p0).unit() * accuracy
        sp = p0
        while (sp - p0).length < seg_length:
            sample_points.append(sp.to_list())
            sp = sp + d

    sample_points.append(track[-1])
    return sample_points


class MotionTrackHold(object):
    def __init__(self, how_long):
        super(MotionTrackHold, self).__init__()
        self.how_long = how_long


class MotionTrackSuper(object):
    def __init__(self, points=None, speed=0.4, is_hold=False):
        super(MotionTrackSuper, self).__init__()
        self.speed = speed
        self.timestamp = 0
        self.event_points = []  # [ts, (x, y), contact_id],  timestamp as arrival time
        self.is_hold = is_hold

        if points:
            for p in points:
                self.move(p)

    @property
    def last_point(self):
        if self.event_points:
            return self.event_points[-1][1]
        return None

    def start(self, p):
        return self.move(p)

    def move(self, p):
        if self.last_point:
            dt = (Vec2(p) - Vec2(self.last_point)).length / self.speed
            self.timestamp += dt
        self.event_points.append([self.timestamp, p, 0])
        return self

    def hold(self, t):
        self.timestamp += t
        if self.event_points:
            self.move(self.last_point)
        return self

    def set_contact_id(self, _id):
        for ep in self.event_points:
            ep[2] = _id

    def discretize(self, contact_id=0, accuracy=0.004, dt=0.01):
        """
        Sample this motion track into discretized motion events.

        Args:
            contact_id: contact point id
            accuracy: motion minimum difference in space
            dt: sample time difference
        """

        if not self.event_points:
            return []

        events = []
        action_dt = accuracy / self.speed
        dt = dt or action_dt

        ep0 = self.event_points[0]
        for _ in range(int(ep0[0] / dt)):
            events.append(['s', dt])
        events.append(['d', ep0[1], contact_id])
        for i, ep in enumerate(self.event_points[1:]):
            prev_ts = self.event_points[i][0]
            curr_ts = ep[0]
            p0 = self.event_points[i][1]
            p1 = ep[1]
            if p0 == p1:
                # hold
                for _ in range(int((curr_ts - prev_ts) / dt)):
                    events.append(['s', dt])
            else:
                # move
                dpoints = track_sampling([p0, p1], accuracy)
                for p in dpoints:
                    events.append(['m', p, contact_id])
                    for _ in range(int(action_dt / dt)):
                        events.append(['s', dt])

        if not self.is_hold:
            events.append(['u', contact_id])
        return events