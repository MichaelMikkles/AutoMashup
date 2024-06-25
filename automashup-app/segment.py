import numpy as np
import copy
from utils import closest_index

# Define a Track class to represent a part of a track
# The aim of this kind of object is to keep together the audio itself,
# and the beats

class Segment:

    transition_time = 0.5 # transition time in seconds

    def __init__(self, segment_dict):
        # We create a segment from a dict coming from metadata.
        # They look like this : 
        # {
        #   "start": 0.4,
        #   "end": 22.82,
        #   "label": "verse"
        # }

        for key in segment_dict.keys():
            setattr(self, key, segment_dict[key])


    def link_track(self, track):
        # Function to link a segment to a track, must be set whenever
        # we create a segment
        # it loads all the pieces of information useful for a segment
        self.sr = track.sr
        beats = track.beats
        downbeats = track.downbeats
        
        start_beat = closest_index(self.start, beats)
        end_beat = closest_index(self.end, beats)

        self.beats = beats[start_beat:end_beat]
        
        if self.beats == []:
            self.downbeats = []
            self.audio = np.array([])
            self.left_transition = np.array([])
            self.right_transition = np.array([])

        else:
            self.beats = self.beats - np.repeat(self.beats[0], len(self.beats))

            self.downbeats = downbeats - np.repeat(downbeats[0], len(downbeats))
            self.downbeats = [downbeat for downbeat in self.downbeats if downbeat in self.beats]
            if self.downbeats != []:
                self.downbeats = self.downbeats - np.repeat(self.downbeats[0], len(self.downbeats))

            self.audio = track.audio[round(self.start*self.sr):round(self.end*self.sr)]

            if self.start - self.transition_time > 0 :
                self.left_transition = track.audio[round((self.start-self.transition_time)*self.sr):round(self.start*self.sr)]
            else :
                self.left_transition = track.audio[:round(self.start*self.sr)]
            if self.end + self.transition_time < len(track.audio) * self.sr:
                self.right_transition = track.audio[round(self.end*self.sr):round((self.end+self.transition_time)*self.sr)]
            else : 
                self.right_transition = track.audio[round(self.end*self.sr):]

    def concatenate(self, segment):
        # Functions to concatenate two segments, and to keep track of beats and downbeats

        # Calculate the transition length (optional, if you need to handle transitions between segments)
        # transition_length = min(len(self.right_transition), len(segment.left_transition))
        

        print(f"Concatenating segment: {self.label} with segment: {segment.label}")
        # Calculate the seconds to shift the incoming beats to start where the current segment's audio ends.
        offset = len(self.audio) / self.sr
        new_beats = segment.beats + offset
        new_downbeats = segment.downbeats + offset

        print(f"Original audio length: {len(self.audio)}, segment audio length: {len(segment.audio)}")
        print(f"Original beats: {self.beats}")
        print(f"Segment beats: {segment.beats}")
        print(f"New beats: {new_beats}")

        # Concatenate the beats array of the current segment
        self.beats = np.concatenate([self.beats, new_beats])

        # Concatenate the downbeats array
        self.downbeats = np.concatenate([self.downbeats, new_downbeats])

        # Concatenate the audio data of the two segments
        self.audio = np.concatenate((self.audio, segment.audio))

        print(f"After concatenation, audio length: {len(self.audio)}, beats length: {len(self.beats)}, downbeats length: {len(self.downbeats)}")



    def get_audio_beat_fitted(self, beat_number):
        """
        Fit the segment to a specified number of beats.

        Parameters:
        - beat_number (int): Number of beats to fit the segment to.

        Returns:
        - fitted_segment (Segment): A copy of the segment fitted to the specified beat number.
        """
        try:
            # Make a deep copy of the segment to avoid modifying the original
            result = copy.deepcopy(self)

            if beat_number == 0:
                # If beat_number is 0, return an empty segment
                result.audio = np.array([])
                result.beats = []
                result.downbeats = []
            else:
                # Ensure the segment's beats match or exceed the target beat_number
                while len(result.beats) < beat_number:
                    result.concatenate(self)

                # Adjust audio length to fit beat_number
                new_length = round(len(result.audio) * (beat_number / len(result.beats)))
                result.audio = result.audio[:new_length]
                result.beats = result.beats[:beat_number]
                result.downbeats = [downbeat for downbeat in result.downbeats if downbeat < result.beats[-1]]

            return result

        except Exception as e:
            # Handle any exceptions gracefully and print detailed error message
            print(f"Error fitting segment {self.label} to {beat_number} beats: {e}")
            # Return None or raise the exception based on your error handling strategy
            raise e  # or return None or handle the error appropriately




