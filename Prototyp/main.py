from function import *

if __name__ == "__main__":

    logged = 1
    pop_up_open = 0
    check_online = ""

    start_stream()

    while 1: 

        try:
            hold()
            check_online = text_XPATH(time_live)
            if ":" in check_online:
                init()
                pass

        except:
            print(f"Max. 15 min waiting")
            hold(700,100)
            driver.refresh()
            pass

        while ":" in check_online:
            try:

                if pop_up_open == 0:
                    click_button(button_my_channel_points)
                    pop_up_open = 1
                
                try:
                    click_button(button_prediction_prompt)                     
                    submission = text_XPATH(text_submission)

                except:
                    print("No prediction found")
                    logged = 0
                    if pop_up_open == 1:
                        click_button(button_my_channel_points)
                        pop_up_open = 0
                    hold(15,15)
                    pass

                if any(keyword in submission for keyword in ["closed", "closing"]):
                    logged = 0
                    
                try:
                    click_button(three_plus_votes)
                    logged == 1
                except:
                    pass

                if (logged == 0) and "ended" in submission:
                    try:
                        click_button(button_see_details)
                    except:
                        pass

                    if get_winner():                     
                        channel_bets_total(0)
                    else:
                        # if 'Red' wins
                        channel_bets_total(1)

                    logged = 1

                if pop_up_open == 1:
                    click_button(button_my_channel_points)
                    pop_up_open = 0
                    hold(15,15)
            
            except:            
                if pop_up_open == 1:
                    click_button(button_my_channel_points)
                    pop_up_open = 0
                hold(2,15)
                pass

            try:
                check_online = text_XPATH(time_live)
                if ":" in check_online:
                    pass

            except:
                check_online = ""
                driver.refresh()
