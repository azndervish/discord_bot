export DISCORD_API_KEY=`aws ssm get-parameter --name discord_bot --region us-east-2 --with-decryption | jq -r .Parameter.Value`
export OPENAI_API_KEY=`aws ssm get-parameter --name openai_api_key --region us-east-2 --with-decryption | jq -r .Parameter.Value`
python3 discord_bot.py