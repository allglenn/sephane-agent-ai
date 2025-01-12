.PHONY: init clean

init:
	# Create main directories
	mkdir -p api/guest_guides
	mkdir -p api/tools
	mkdir -p react-app/public
	mkdir -p react-app/src

	# Create API files
	touch api/app.py
	touch api/requirements.txt
	touch api/Dockerfile
	
	# Create tools files
	touch api/tools/__init__.py
	touch api/tools/search_tool.py
	touch api/tools/user_tool.py
	
	# Create environment files
	if [ ! -f api/.env ]; then \
		echo "OPENAI_API_KEY=your-openai-api-key-goes-here" > api/.env; \
		echo "FLASK_DEBUG=False" >> api/.env; \
		echo "PORT=5000" >> api/.env; \
	fi
	
	# Create .env.example
	echo "# OpenAI API Configuration" > api/.env.example
	echo "OPENAI_API_KEY=your-openai-api-key-here" >> api/.env.example
	echo "" >> api/.env.example
	echo "# Flask Configuration" >> api/.env.example
	echo "FLASK_DEBUG=False" >> api/.env.example
	echo "PORT=5000" >> api/.env.example
	
	# Create guest guide PDFs
	touch api/guest_guides/guest_guide_check_in.pdf
	touch api/guest_guides/guest_frequently_asked.pdf
	touch api/guest_guides/guest_activity_recommendations.pdf

	# Create React files
	cp react-app/template/* react-app/public/
	cp react-app/template/* react-app/src/
	touch react-app/package.json
	touch react-app/package-lock.json
	touch react-app/Dockerfile

	# Create docker-compose file
	touch docker-compose.yml

	# Create gitignore
	touch .gitignore

	@echo "Project structure created successfully!"
	@echo "IMPORTANT: Don't forget to update your OPENAI_API_KEY in api/.env"

clean:
	rm -rf api
	rm -rf react-app
	rm -f docker-compose.yml
	rm -f .gitignore
	@echo "Project structure cleaned successfully!"
