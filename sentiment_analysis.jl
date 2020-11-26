using TextAnalysis 
using TextAnalysis: NaiveBayesClassifier, fit!, predict
using DataFrames
using CSV
using MLDataUtils

#Load Data -------------------------------------------------------------------------
dir = "Disaster_Social_Media_Analysis"
data = CSV.read(joinpath(dir,"Data","Taal_200111_200119_en_PH_labeled.csv"))

names(data)

#Prepare data ---------------------------------------------------------------------
df = select(data,:tweet,:sentiment_labels)
replace.(df[:sentiment_labels],1 => "positive")

df[:sentiment_labels] = map(df[:sentiment_labels]) do x
	if x == 1 return "positive" 
	elseif x == -1 return "negative" 
	else "neutral"
	end
end

#Extract hashtags, urls and @calls -------------------------------------------------
regExp = Dict{Symbol,Regex}(
	:mentions => r"@\w+",
	:hashtags => r"#\w+",
	:urls => r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

# Function to extract tokens
function extract_tokens(s::String,token_type::Symbol)::Array{String}
	return collect(x.match for x in eachmatch(regExp[token_type], s))
end

# Function to clean text
function remove_tokens(s::String)::String
	for re in values(regExp)
		s = replace(s, re => "")
	end
	return s
end

#Add a column with cleaned text to DataFrames
df.mentions = extract_tokens.(df.tweet,:mentions)
df.hashtags = extract_tokens.(df.tweet,:hashtags)
df.url = extract_tokens.(df.tweet,:urls)
df.clean_text = remove_tokens.(df.tweet)

#Train and Testing data ---------------------------------------------------------------
train_df,test_df = splitobs(shuffleobs(df), at = 0.7)
names(test_df)

#Preprocessing ------------------------------------------------------------------------
function create_string_doc(s::String)::StringDocument
	sd = StringDocument(s)
	op = 0x00
	op |= strip_punctuation
	op |= strip_stopwords
	prepare!(sd,op)
	return sd
end

#Fit Model ---------------------------------------------------------------------------
model = let 
	bayes = NaiveBayesClassifier(unique(df[:sentiment_labels]))

	for (tw,lab) in zip(train_df.tweet,train_df.sentiment_labels)
		sd = create_string_doc(tw)
		fit!(bayes,sd,lab)
	end
	bayes
end

#Predictions -----------------------------------------------------------------------
function predict_on_test_data_1(model::NaiveBayesClassifier, test_df::SubDataFrame)::DataFrame
	df = copy(test_df)
	cleaned_text = TextAnalysis.text.(create_string_doc.(remove_tokens.(df[:tweet])))
	df.prob_score = predict.(Ref(model),cleaned_text)

	df.positive = getindex.(df.prob_score,"positive")
	df.negative = getindex.(df.prob_score,"negative")
	df.neutral = getindex.(df.prob_score,"neutral")

	select!(df, Not(:prob_score))
	return df
end

function predict_and_choose(c::NaiveBayesClassifier, sd::StringDocument)
    val = predict(c,sd)
    return argmax(val)
end

yhat = let 
    sds = create_string_doc.(lowercase.(remove_tokens.(test_df.tweet)))
    predict_and_choose.(Ref(model), sds)
end

pred_df = predict_on_test_data_1(model,test_df)

correct_predictions = count(pred_df[:sentiment_labels] .== yhat)
incorrect_predictions = nrow(test_df) - correct_predictions


