# ViewRewrite

**ViewRewrite** addresses the issue of excessive view generation in multi-relation, multi-query scenarios, reducing overall differential privacy costs through query rewriting. By converting nested and derived table queries into equivalent alternative forms, it avoids view proliferation caused by changes in subquery conditions.

## Key Features
- **Differential Privacy Guarantee**: Effectively controls privacy loss in multi-relation, multi-query scenarios.
- **Efficient View Management**: Minimizes redundant view generation and improves generation efficiency.
- **Query Rewriting Engine**: Rewrites complex queries into equivalent forms while preserving query results.
- **Cross-Platform Compatibility**: Compatible with various database platforms.

## Installation

**1. Clone the Repository:**

   First, clone the repository:

   ```bash
   git clone https://github.com/xinglindu/ViewRewrite.git
   ```

   Then navigate to the project directory:

   ```bash
   cd ViewRewrite
   ```

**2. Install Dependencies:**

   Inside the project directory, install the Python dependencies with the following command:

   ```bash
   pip install -r requirements.txt
   ```

**3. Install a Database System:**

   It is recommended to use PostgreSQL as the database system for this project. Alternatively, you can choose any other relational database, such as MySQL, SQLite, MariaDB, or Microsoft SQL Server, depending on your preference or project requirements.

## Usage

**1. Import Data:**

   Import a sample dataset into your database to get started. Recommended datasets include:

   - **TPC-H Dataset**: A benchmark for decision support systems. You can download it from [here](https://www.tpc.org/tpch/).
   - **US Dataset**: A collection of diverse datasets. You can find it at [this link](https://doi.org/10.3886/E100274V1).

   Follow the instructions provided on these websites to download and import the data into your database system.

**2. Maintain Constraints:**

   Define and maintain constraints between relations, such as primary keys, foreign keys, and other dependencies, to ensure data integrity.

**3. Write Query Test Cases:**

   Create a set of test queries to validate the functionality and performance of the system. Include different types of queries such as:

   - Single Relation Queries
   - Join Queries
   - Correlated Subqueries
   - Non-correlated Subqueries
   - Derived Table Queries

**4. Define Primary Privacy-Protecting Relations and Privacy Budget:**

   Identify the main relations that require privacy protection and set up the privacy budget (i.e., epsilon value for differential privacy).

**5. Experimental Testing:**

   - **dataProtection:** Generate private synopses using differential privacy techniques to protect sensitive data.
   - **accessControl:** Handle user-submitted queries and apply privacy-preserving mechanisms.
   - **experimentAnalysis:** Analyze and evaluate experimental results to assess the system's effectiveness and performance.

   Ensure that Python has all the necessary libraries installed for database interaction, data processing, privacy protection, and experimental analysis.

## Experimental Results
Experiments on real-world datasets show that ViewRewrite significantly reduces the number of views, lowers privacy costs, and maintains high data utility.

## Contact
For inquiries, please reach out to [xinglin@mail.sdu.edu.cn](mailto:xinglin@mail.sdu.edu.cn).