from utils import increase_array_size
import librosa
import numpy as np

# Mashup Technics
# In this file, you may add mashup technics
# the input of such a method is a list of up to 4 objects of type Track. 
# You can modify them without making any copy, it's already done before.
# You may find useful methods in the track.py file
# Be sure to return a Track object

def mashup_technic(tracks, repitch=False, phase_fit=False):
    # Mashup technic with first beat alignment and bpm sync
    sr = tracks[0].sr # The first track is used to determine the target bpm
    tempo = tracks[0].bpm
    main_track_length = len(tracks[0].audio)
    beginning_instant = tracks[0].beats[0] # beats metadata
    beginning = beginning_instant * sr
    mashup = np.zeros(0)
    mashup_name = ""

    # we add each track to the mashup
    for track in tracks:
        mashup_name += track.name + " " # name
        track_tempo = track.bpm
        if track == tracks[0]:
            track_beginning_temporal = track.beats[0]
        else:
            track_beginning_temporal = track.downbeats[0]
        track_sr = track.sr
        track_beginning = track_beginning_temporal * track_sr
        track_audio = track.audio

        # reset first beat position
        print("***********Track beginning : ", track_beginning_temporal)
        track_audio_no_offset = np.array(track_audio)[round(track_beginning):] 

        # multiply by bpm rate if there is no phase fit
        if not phase_fit:
            track_audio_accelerated = librosa.effects.time_stretch(track_audio_no_offset, rate = tempo / track_tempo)
        else:
            track_audio_accelerated = track_audio_no_offset

        # mashup technic which repiches every track to the first one
        if repitch == True and track != tracks[0]:
            key = tracks[0].get_key() # target key
            track_audio_accelerated = track.pitch_track(key, track_audio_accelerated) # repitch

        # add the right number of zeros to align with the main track
        final_track_audio = np.concatenate((np.zeros(round(beginning)), track_audio_accelerated)) 

        size = max(len(mashup), len(final_track_audio))
        mashup = np.array(mashup)
        mashup = (increase_array_size(final_track_audio, size) + increase_array_size(mashup, size))

    # Adjust mashup length to be the same as the main track's audio length
    if len(mashup) > main_track_length:
        mashup = mashup[:main_track_length]
    else:
        mashup = increase_array_size(mashup, main_track_length)

    
    

    # we return a modified version of the first track
    # doing so, we keep its metadata
    tracks[0].audio = mashup

    return tracks[0]


def mashup_technic_repitch(tracks):
    # standard mashup method calling repitch
    return mashup_technic(tracks, repitch=True)


def mashup_technic_fit_phase(tracks, repitch = False):
    # Mashup technique with phase alignment (i.e., chorus with chorus, verse with verse...)
    # Each track's structure is aligned with the first one
    
    for i in range(len(tracks) - 1):
        tracks[i + 1].fit_phase(tracks[0])

    # Standard mashup method
    return mashup_technic(tracks, repitch, phase_fit=True)

def mashup_technic_fit_phase_repitch(tracks):
    # Mashup technique with phase alignment and repitch
    # Phase fit mashup
    return mashup_technic_fit_phase(tracks, repitch = True)
