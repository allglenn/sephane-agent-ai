.PHONY: init clean

init:
	# Create main directories
	mkdir -p api/guest_guides
	mkdir -p react-app/public
	mkdir -p react-app/src

	# Create API files
	touch api/app.py
	touch api/requirements.txt
	touch api/Dockerfile
	
	# Create guest guide PDFs
	touch api/guest_guides/guest_guide_check_in.pdf
	touch api/guest_guides/guest_frequently_asked.pdf
	touch api/guest_guides/guest_activity_recommendations.pdf

	# Create React files
	touch react-app/package.json
	touch react-app/package-lock.json
	touch react-app/Dockerfile

	# Create docker-compose file
	touch docker-compose.yml

	@echo "Project structure created successfully!"

clean:
	rm -rf api
	rm -rf react-app
	rm -f docker-compose.yml
	@echo "Project structure cleaned successfully!"
