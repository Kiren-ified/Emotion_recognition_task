from psychopy.sound import Sound
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim
from psychopy.core import Clock, quit, wait
import pandas as pd
from psychopy.event import getKeys, clearEvents

#dialogue box routine
exp_info = {'participant_id': '', 'age': '', 'current_emotional_state':''}
dlg = DlgFromDict(exp_info)

#Ending the experiment if okay is not pressed
if not dlg.OK:
    quit()

#initialize window and clock
win = Window(size=(1000, 800), fullscr=False)
clock = Clock()

# Create a welcome screen and show for 3 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", color=(0, 1, 1), font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(3)

#Instructions
instruct_txt = """ 
In this experiment, you will see faces and hear a brief audio clip with words and non-words. 
Both the face and audio will express any one of these emotions: Happiness, Anger, Sadness, Fear, and Disgust. 

Importantly, you need to respond to the expression in the voice and ignore the face. You respond with the letter keys:
    
    HAPPINESS = H
    ANGER = A
    SADNESS = S
    FEAR = F
    DISGUST = D
    
To start the experiment, press 'Enter'
 """
# Show instructions and wait until response
instruct_txt = TextStim(win, instruct_txt, alignText='left', height=0.085)
instruct_txt.draw()
win.flip()

while True:
    if 'return' in getKeys():
        break  
 
#create an emotion map dictionary
emotion_map = {'h' : 'happiness', 'a' : 'anger', 's' : 'sadness', 'd' : 'disgust', 'f' : 'fear'}

#Create fixation target
fix_target = TextStim(win, '+')
trial_clock = Clock()

#read in the excel sheet
cond_df = pd.read_excel('Conditions.xlsx')
cond_df = cond_df.sample(frac=1)

###TRIAL ROUTINE###
for idx, row in cond_df.iterrows():
    # Extract face and voice
    curr_face = row['F_Stimuly']
    curr_voice = row['V_Stimuly']
    corr_resp = row['V_emotion']
    
    trial_clock.reset()
    
    while trial_clock.getTime() <0.5:
        fix_target.draw()
        win.flip()
        
    trial_clock.reset()
    clearEvents()
            
    stim_img = ImageStim(win, curr_face)
    stim_img.size = 0.5  # make a bit smaller
    stim_voice = Sound(curr_voice, stereo=True, hamming=True, secs=2)
    stim_voice.setVolume(3.0) #make the volume audible
    
    stim_voice.play()
    stim_img.draw()
    
    win.flip()
    response = ''
    found_response=False
    rt=0
    is_correct = 0
    while trial_clock.getTime() <5 and found_response is False:
        keys=getKeys()
        for key in keys:
            if 'escape' in keys:
                win.close()
                quit()
            if key in ['a', 's', 'f', 'd', 'h']:
                print(f"you've selected the {emotion_map[key]} emotion")
                response = emotion_map[key]
                rt=round(trial_clock.getTime(),3)
                found_response=True
                if response == corr_resp:
                    is_correct = 1
                else:
                    is_correct = 0
                    
                break
    #create columns in the excel sheet to record responses
    cond_df.loc[idx, 'response'] = response
    cond_df.loc[idx, 'reaction_time'] = rt
    cond_df.loc[idx, 'correct'] = is_correct
    
#calculate mean rt and total number of correct responses
effect = cond_df.groupby('In_Cong')['reaction_time'].mean()
total_score = cond_df.groupby('In_Cong')['correct'].sum()

#print results on console
print(effect)
print(total_score)

#print results to the window
resp_string = "Your results are: \n" #create a string that can be added onto
for condition, mean_rt in effect.items():
    if condition == "CONG": #rename the titles from the label in the excel sheet to a more readable format
        condition = "congruent reaction time" 
    else:
        condition = "incongruent reaction time"
    resp_string += f"{condition}: {mean_rt:.3f} seconds\n" #adds the new information to the previously established resp_string

for condition, score_sum in total_score.items():
    if condition == "CONG":
        condition = "congruent correct"
    else:
        condition = "incongruent correct"
    resp_string += f"{condition}: {score_sum} correct\n"
    
#print results
result_txt = TextStim(win, resp_string, color = (0,1,1))
result_txt.draw()
win.flip()
wait(7)

#Good-bye message
bye_txt = TextStim(win, "Thank you for your participation!", color = (0,1,1))
bye_txt.draw()
win.flip()
wait(2)

#save data from the experiment to the file
cond_df.to_csv(f"sub-{exp_info['participant_id']}.csv")

win.close()
quit()